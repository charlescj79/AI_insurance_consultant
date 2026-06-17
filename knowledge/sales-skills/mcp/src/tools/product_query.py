#!/usr/bin/env python3
"""Tool 1: 产品条款查询 (insurance_product_query)"""
import json, os, re
from typing import Optional, Dict, Any

_DB_PATH = None

def _get_db_path():
    global _DB_PATH
    if _DB_PATH:
        return _DB_PATH
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(os.path.dirname(script_dir))
    db_path = os.path.join(parent_dir, "cli", "product-clauses-db.json")
    _DB_PATH = db_path
    return db_path

def load_product_db():
    """加载产品数据库"""
    db_path = _get_db_path()
    try:
        with open(db_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("products", [])
    except FileNotFoundError:
        return []

def _fuzzy_match_product(query: str, products: list) -> Optional[dict]:
    """模糊匹配产品名称"""
    query_lower = query.lower().strip()
    if not query_lower:
        return None
    for p in products:
        if p["name_cn"] == query or p["id"].lower() == query_lower:
            return p
    candidates = []
    for p in products:
        name = p["name_cn"].lower()
        en_name = p.get("name_en", "").lower()
        if query_lower in name or query_lower in en_name:
            score = 3 if query_lower == name else 1
            candidates.append((score, p))
    for p in products:
        en_short = "".join([c[0] for c in p.get("name_en", "").split() if c.isalpha()]).lower()
        if query_lower == en_short:
            candidates.append((2, p))
    if not candidates and query_lower:
        for p in products:
            name = p["name_cn"]
            overlaps = sum(1 for ch in query_lower if ch.lower() in name.lower())
            threshold = max(1, len(query) // 2)
            if overlaps >= threshold:
                candidates.append((1, p))
    if candidates:
        candidates.sort(key=lambda x: -x[0])
        return candidates[0][1]
    return None

def handle_product_query(params: dict) -> Dict[str, Any]:
    """Tool 1 handler: insurance_product_query"""
    action = params.get("action")
    products = load_product_db()
    if not products:
        return {"error": "product_db_not_found"}

    if action == "list":
        output = {
            "products_compared": len(products),
            "products": [
                {"id": p["id"], "name_cn": p["name_cn"], "insurance_type": p["insurance_type"],
                 "category": p["category"], "coverage_summary": p.get("coverage_summary", "")[:100]}
                for p in products
            ],
            "usage_hint": "使用 detail action + product_name 查询详情"
        }
    elif action == "detail":
        product = _fuzzy_match_product(params.get("product_name", ""), products)
        if not product:
            return {"error": "product_not_found", "available_products": [p["name_cn"] for p in products]}
        output = {
            "id": product["id"], "name_cn": product["name_cn"],
            "insurance_type": product["insurance_type"], "category": product["category"],
            "coverage_summary": product.get("coverage_summary", ""),
            "detailed_coverage": product.get("detailed_coverage", "详见条款说明"),
            "exclusions": product.get("exclusions", []),
            "suitable_for": product.get("suitable_for", []),
            "compliance_points": product.get("compliance_points", ["依合同约定给付保险金"]),
            "common_questions": product.get("common_questions", []),
            "regulatory_refs": product.get("regulatory_refs", []),
        }
    else:
        output = {"error": "invalid_action", "available_actions": ["list", "detail"]}
    return {"result": output}
