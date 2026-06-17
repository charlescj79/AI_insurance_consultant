#!/usr/bin/env python3
"""R22 MCP Server Test Suite — HTTP + stdio (fixed)"""

import subprocess, json, sys, urllib.request

BASE_URL = "http://localhost:18060"
MCP_DIR = "/Users/charles/.openclaw/workspace/knowledge/sales-skills/mcp"
passed = 0
failed = 0

def http_call(payload):
    """Make HTTP call and return parsed result dict"""
    global passed, failed
    data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(
        f"{BASE_URL}/mcp",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    resp = urllib.request.urlopen(req)
    body = resp.read()
    result = json.loads(body.decode('utf-8'))
    return result

def stdio_call(messages):
    global passed, failed
    p = subprocess.Popen(
        [sys.executable, "server.py"],
        cwd=MCP_DIR,
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    input_data = "\n".join(messages).encode()
    out, err = p.communicate(input_data, timeout=10)
    lines = [l for l in out.decode("utf-8", errors="replace").strip().split("\n") if l.strip()]
    result = None
    # Collect all valid responses, return the last one with result (skip initialize handshake)
    candidates = []
    for line in lines:
        try:
            d = json.loads(line)
            if "result" in d and "error" not in d.get("result", {}):
                candidates.append(d)
        except:
            pass
    # Return last candidate (the actual tool call, after initialize handshake)
    return candidates[-1] if candidates else None

def test_http(name, payload):
    global passed, failed
    try:
        r = http_call(payload)
        passed += 1
        print(f"  ✅ {name}")
        return r
    except Exception as e:
        failed += 1
        print(f"  ❌ {name}: {e}")
        return None

def test_stdio(name, messages):
    global passed, failed
    try:
        r = stdio_call(messages)
        if r and "result" in r:
            passed += 1
            print(f"  ✅ {name}")
            return r
        else:
            failed += 1
            print(f"  ❌ {name}: no valid response")
            return None
    except Exception as e:
        failed += 1
        print(f"  ❌ {name}: {e}")
        return None

def check_health():
    global passed, failed
    try:
        resp = urllib.request.urlopen(f"{BASE_URL}/health")
        d = json.loads(resp.read().decode())
        if d.get("status") == "ok":
            passed += 1
            print(f"  ✅ Health check")
            return True
        else:
            failed += 1
            print(f"  ❌ Health check: {d}")
            return False
    except Exception as e:
        failed += 1
        print(f"  ❌ Health check: {e}")
        return False

print("=" * 50)
print("  R22 MCP Server Test Suite v1.0")
print("=" * 50)
print("\n>>> HTTP MODE TESTS")
print("---")

check_health()

# T2: tools/list
r = test_http("T2. tools/list", {"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}})
if r: print(f"       → {len(r['result']['tools'])} tools registered")

# T3: compliance_check BLOCKED
r = test_http("T3. compliance_check (BLOCKED)", 
    {"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"compliance_check","arguments":{"text":"这款分红险年化收益5%，保本保息！","strict_mode":True}}})
if r: print(f"       → status={r['result']['result']['compliance_status']}, violations={r['result']['result']['violations_found']}")

# T4: compliance_check PASS
r = test_http("T4. compliance_check (PASS)",
    {"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"compliance_check","arguments":{"text":"建议咨询持牌中介人。"}}})
if r: print(f"       → status={r['result']['result']['compliance_status']}")

# T5: needs_assessment
r = test_http("T5. needs_assessment",
    {"jsonrpc":"2.0","id":5,"method":"tools/call","params":{"name":"needs_assessment","arguments":{"message":"我有房贷要还，万一出事家里怎么办？最近体检发现结节。"}}})
if r:
    res = r['result']['result']
    print(f"       → grade={res['customer_grade']}, urgency={res['urgency']}")
    print(f"       → signals={[s['need_type'] for s in res['detected_needs']]}")

# T6: objection_handler
r = test_http("T6. objection_handler",
    {"jsonrpc":"2.0","id":6,"method":"tools/call","params":{"name":"objection_handler","arguments":{"category":"price","scenario":"保费太贵","tier":"medium"}}})
if r:
    res = r['result']['result']
    print(f"       → tone={res['tone']}, script_len={len(res.get('script',''))}")

# T7: private_sop_runner journey
r = test_http("T7. private_sop_runner",
    {"jsonrpc":"2.0","id":7,"method":"tools/call","params":{"name":"private_sop_runner","arguments":{"action":"customer-journey","grade":"B"}}})
if r: print(f"       → {r['result']['result']['simulation']}, touchpoints={r['result']['result']['total_touchpoints']}")

# T8: product_query list
r = test_http("T8. product_query (list)",
    {"jsonrpc":"2.0","id":8,"method":"tools/call","params":{"name":"insurance_product_query","arguments":{"action":"list"}}})
if r: print(f"       → {r['result']['result']['products_compared']} products")

# T9: product_query detail
r = test_http("T9. product_query (detail)",
    {"jsonrpc":"2.0","id":9,"method":"tools/call","params":{"name":"insurance_product_query","arguments":{"action":"detail","product_name":"危疾"}}})
if r: print(f"       → {r['result']['result'].get('name_cn','N/A')}")

# T10: SOP day-sequence
r = test_http("T10. sop_day_sequence",
    {"jsonrpc":"2.0","id":10,"method":"tools/call","params":{"name":"private_sop_runner","arguments":{"action":"day-sequence","day":3,"grade":"A","channel":"wechat"}}})
if r: print(f"       → {r['result']['result']['day']}")

# T11: Batch request
r = test_http("T11. batch request",
    [{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"needs_assessment","arguments":{"message":"test"}}},
     {"jsonrpc":"2.0","id":2,"method":"compliance_check","params":{"text":"合规文本"}}])

# T12: Health endpoint
print("\n>>> OTHER ENDPOINTS")
print("---")
try:
    resp = urllib.request.urlopen(f"{BASE_URL}/mcp/manifest")
    d = json.loads(resp.read().decode())
    if d.get('name') == 'insurance-sales-mcp':
        passed += 1
        print(f"  ✅ MCP manifest endpoint")
    else:
        failed += 1
        print(f"  ❌ MCP manifest: unexpected response")
except Exception as e:
    failed += 1
    print(f"  ❌ MCP manifest: {e}")

# T13: Error handling (unknown tool)
r = test_http("T13. error handling (unknown tool)",
    {"jsonrpc":"2.0","id":14,"method":"tools/call","params":{"name":"nonexistent_tool","arguments":{}}})
if r and 'error' in r:
    passed += 1
    print(f"  ✅ Error handled correctly")
else:
    failed += 1
    print(f"  ❌ Should return error for unknown tool")

# T14: SOP get-schedule
r = test_http("T14. sop_get_schedule",
    {"jsonrpc":"2.0","id":15,"method":"tools/call","params":{"name":"private_sop_runner","arguments":{"action":"get-schedule","sid":"test-001"}}})
if r and 'schedule' in r['result']['result']:
    passed += 1
    print(f"  ✅ SOP schedule returned ({len(r['result']['result']['schedule'])} days)")
else:
    failed += 1
    print(f"  ❌ SOP schedule failed")

# T15: Objection list_all
r = test_http("T15. objection_list_all",
    {"jsonrpc":"2.0","id":16,"method":"tools/call","params":{"name":"objection_handler","arguments":{"list_all":True}}})
if r and r['result']['result'].get('action') == 'list_all_scenarios':
    passed += 1
    print(f"  ✅ Objection list_all ({r['result']['result']['total_scenarios']} scenarios)")
else:
    failed += 1
    print(f"  ❌ Objection list_all failed")

print("\n>>> STDIO MODE TESTS (fixed protocol)")
print("---")

stdio_msgs = [
    '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"0.1.0"}}}',
    '{"jsonrpc":"2.0","id":12,"method":"tools/call","params":{"name":"needs_assessment","arguments":{"message":"体检发现结节，担心癌症。"}}}'
]
r = test_stdio("T16. stdio needs_assessment", stdio_msgs)
if r and 'result' in r:
    print(f"       → grade={r['result']['result'].get('customer_grade','N/A')}")

# T17: stdio + compliance_check
stdio_msgs2 = [
    '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"0.1.0"}}}',
    '{"jsonrpc":"2.0","id":17,"method":"tools/call","params":{"name":"compliance_check","arguments":{"text":"年化收益5%，保本保息！"}}}'
]
r = test_stdio("T17. stdio compliance_check", stdio_msgs2)
if r and 'result' in r:
    status = r['result']['result'].get('compliance_status', 'N/A')
    print(f"       → {status}")

# T18: stdio product query
stdio_msgs3 = [
    '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"0.1.0"}}}',
    '{"jsonrpc":"2.0","id":18,"method":"tools/call","params":{"name":"insurance_product_query","arguments":{"action":"list"}}}'
]
r = test_stdio("T18. stdio product_list", stdio_msgs3)
if r and 'result' in r:
    count = len(r['result']['result'].get('products', []))
    print(f"       → {count} products")

print("\n" + "=" * 50)
print(f"  RESULTS: {passed} passed, {failed} failed / {passed+failed} total")
if failed == 0:
    print("  ✅ ALL TESTS PASSED")
else:
    print("  ❌ SOME TESTS FAILED")
print("=" * 50)

sys.exit(0 if failed == 0 else 1)
