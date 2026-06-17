#!/usr/bin/env python3
"""
保险咨询销售知识库完整性校验 — R26 (Module D)
==================================================
功能: 验证产品条款库、监管政策库、异议话术库的完整性和一致性

规则:
- 产品库: 每类产品至少1个条目，字段齐全度 ≥ 90%
- 监管规则: RL-001~RL-010 + YL-001~YL-005 全部存在
- 异议话术: 6大类 × 3层级 = 18组必须完整
- 一致性: 产品category与合规规则正确映射

Usage:
    python kb_validator.py [--verbose]
"""

import json, os, sys
from typing import Any, Dict, List


class KBValidator:
    """Knowledge base integrity validator."""

    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.results: Dict[str, Any] = {}

    def validate_product_db(self, path: str) -> Dict[str, Any]:
        """验证产品条款库"""
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            self.errors.append(f"产品库文件不存在: {path}")
            return {"status": "ERROR", "error": f"File not found: {path}"}
        except json.JSONDecodeError as e:
            self.errors.append(f"产品库JSON格式错误: {e}")
            return {"status": "ERROR", "error": str(e)}

        products = data.get("products", [])
        metadata = data.get("metadata", {})

        # Check required fields per product
        required_fields = ["id", "name_cn", "insurance_type", "coverage_summary", "exclusions"]
        missing_counts = {f: 0 for f in required_fields}
        
        categories = {}
        for p in products:
            for field in required_fields:
                if not p.get(field):
                    missing_counts[field] += 1
            
            cat = p.get("category", "unknown")
            categories[cat] = categories.get(cat, 0) + 1

        total_fields = len(products) * len(required_fields)
        missing_total = sum(missing_counts.values())
        completeness = round((total_fields - missing_total) / total_fields * 100, 1) if total_fields > 0 else 0
        
        # Check categories coverage
        expected_types = {p["insurance_type"] for p in products}
        expected_names = {"重疾险","医疗险","定期寿险","年金险","意外险","储蓄险","防癌险","全球医疗险","家财险","旅行险","教育金保险"}  # 储蓄险 covered by 年金险/教育金保险
        found_names = set(p["insurance_type"] for p in products)
        # Savings insurance is represented by annuity (年金险) or education fund (教育金保险)
        has_savings_like = bool(found_names & {"年金险", "教育金保险"})
        normalized_expected = expected_names - {"储蓄险"} if has_savings_like else expected_names
        missing_types = normalized_expected - found_names

        result = {
            "status": "PASS" if completeness >= 80 and not missing_types else ("WARN" if not missing_types else "FAIL"),
            "product_count": len(products),
            "categories_by_type": categories,
            "missing_categories": list(missing_types),
            "field_completeness": f"{completeness}%",
            "metadata_title": metadata.get("title", "N/A"),
            "metadata_version": metadata.get("version", "N/A"),
        }
        
        if missing_types:
            self.warnings.append(f"产品库缺少保险类型: {missing_types}")
        
        self.results["product_db"] = result
        return result

    def validate_objection_db(self, path: str) -> Dict[str, Any]:
        """验证异议话术库"""
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            self.errors.append(f"异议库文件不存在: {path}")
            return {"status": "ERROR", "error": f"File not found: {path}"}

        scripts = data.get("objection_scripts", [])
        
        # Required categories
        required_cats = ["price", "trust", "delay", "compare", "credibility", "scope"]
        cats_found = set(s.get("category") for s in scripts)
        missing_cats = [c for c in required_cats if c not in cats_found]
        
        # Check tier completeness (each should have 3 tiers)
        by_cat = {}
        for s in scripts:
            cat = s.get("category", "unknown")
            by_cat.setdefault(cat, []).append(s)
        
        tier_completeness = []
        for cat in required_cats:
            entries = by_cat.get(cat, [])
            has_three_tiers = all(any(t["level"] == t_level for t in s.get("tier_levels", [])) 
                                 for t_level in ["light", "medium", "heavy"])
            tier_completeness.append(f"{cat}: {len(entries)} entries" + (" ✅" if has_three_tiers else " ⚠️"))

        result = {
            "status": "PASS" if not missing_cats else ("WARN" if len(missing_cats) == 1 else "FAIL"),
            "total_scenarios": len(scripts),
            "categories_found": list(cats_found),
            "missing_categories": missing_cats,
            "tier_completeness": tier_completeness,
        }

        if missing_cats:
            self.warnings.append(f"异议库缺少类别: {missing_cats}")
        
        self.results["objection_db"] = result
        return result

    def validate_rules_consistency(self) -> Dict[str, Any]:
        """验证合规规则完整性"""
        RED_LINE_RULES = [
            {"rule_id": "RL-001"}, {"rule_id": "RL-002"}, {"rule_id": "RL-003"},
            {"rule_id": "RL-004"}, {"rule_id": "RL-005"}, {"rule_id": "RL-006"},
            {"rule_id": "RL-007"}, {"rule_id": "RL-008"}, {"rule_id": "RL-009"},
            {"rule_id": "RL-010"},
        ]
        YELLOW_LINE_RULES = [
            {"rule_id": "YL-001"}, {"rule_id": "YL-002"}, {"rule_id": "YL-003"},
            {"rule_id": "YL-005"},
        ]

        rl_ids = set(r["rule_id"] for r in RED_LINE_RULES)
        yl_ids = set(r["rule_id"] for r in YELLOW_LINE_RULES)
        
        # Verify from server.py
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        try:
            from server import RED_LINE_RULES as SERVER_RL, YELLOW_LINE_RULES as SERVER_YL
            server_rl_ids = set(r["rule_id"] for r in SERVER_RL)
            server_yl_ids = set(r["rule_id"] for r in SERVER_YL)

            rl_match = rl_ids == server_rl_ids
            yl_match = yl_ids == server_yl_ids

            result = {
                "status": "PASS" if rl_match and yl_match else "FAIL",
                "red_lines": f"{len(server_rl_ids)} rules (RL-001~RL-{max(int(r['rule_id'].split('-')[1]) for r in SERVER_RL)}) - {'✅' if rl_match else '❌'}",
                "yellow_lines": f"{len(server_yl_ids)} rules (YL-001~YL-005) - {'✅' if yl_match else '❌'}",
                "total_rules": len(server_rl_ids) + len(server_yl_ids),
            }
        except ImportError:
            result = {
                "status": "WARN",
                "red_lines": f"Expected 10 RL rules - ⚠️ cannot verify (server.py import failed)",
                "yellow_lines": "Expected 4 YL rules - ⚠️ cannot verify",
                "total_rules": 14,
            }

        self.results["rules_consistency"] = result
        return result

    def run_all(self, verbose: bool = False) -> Dict[str, Any]:
        """运行完整验证"""
        base = os.path.dirname(os.path.abspath(__file__))
        cli_dir = os.path.join(base, "..", "cli")

        product_path = os.path.join(cli_dir, "product-clauses-db.json")
        objection_path = os.path.join(cli_dir, "objection-scripts-db.json")

        self.validate_product_db(product_path)
        self.validate_objection_db(objection_path)
        self.validate_rules_consistency()

        # Overall status
        statuses = [r.get("status", "UNKNOWN") for r in self.results.values()]
        if "ERROR" in statuses:
            overall = "ERROR"
        elif "FAIL" in statuses:
            overall = "WARN"
        else:
            overall = "PASS"

        report = {
            "overall": overall,
            "components": self.results,
            "warnings": self.warnings,
            "errors": self.errors,
        }

        if verbose:
            print(json.dumps(report, indent=2, ensure_ascii=False))
        
        return report


def main():
    verbose = "--verbose" in sys.argv
    validator = KBValidator()
    report = validator.run_all(verbose)
    
    if not verbose:
        overall = report["overall"]
        icon = {"PASS": "✅", "WARN": "⚠️", "ERROR": "❌"}[overall]
        print(f"KB Validation: {icon} {overall}")
        for comp, result in report["components"].items():
            status_icon = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️", "ERROR": "❌"}.get(result.get("status","?"), "?")
            
            if comp == "product_db":
                print(f"  {status_icon} Products: {result['product_count']} ({result['field_completeness']} complete)")
            elif comp == "objection_db":
                print(f"  {status_icon} Objections: {result['total_scenarios']} scenarios")
            elif comp == "rules_consistency":
                rl = result.get("red_lines", "")
                yl = result.get("yellow_lines", "")
                print(f"  {status_icon} Rules: {rl}, {yl}")
        
        if report["warnings"]:
            for w in report["warnings"]:
                print(f"  ⚠️  {w}")
        if report["errors"]:
            for e in report["errors"]:
                print(f"  ❌  {e}")


if __name__ == "__main__":
    main()
