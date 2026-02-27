#!/usr/bin/env python3
"""
OMG Payment - 付款通知驗證工具

使用方法：
    python3 verify_payment.py --payment-no <payment_no> [選項]

範例：
    python3 verify_payment.py --payment-no "202602270001"

驗證 stdin 輸入的 CheckMacValue 是否正確
"""

import hashlib
import sys
import argparse


# .NET URL Encoding 替換表格
DOTNET_REPLACEMENTS = {
    "%2d": "-", "%5f": "_", "%2e": ".", "%21": "!", "%2a": "*", "%28": "(", "%29": ")",
}


def generate_check_mac_value(params, hash_key, hash_iv):
    """生成 OMG CheckMacValue（SHA256）"""
    filtered = {k: v for k, v in params.items() if k != "CheckMacValue" and v}
    sorted_keys = sorted(filtered.keys(), key=lambda k: k.lower())
    param_str = "&".join(f"{k}={filtered[k]}" for k in sorted_keys)
    raw = f"{hash_key}&{param_str}&{hash_iv}"
    encoded = quote(raw, safe="").lower()
    for old, new in DOTNET_REPLACEMENTS.items():
        encoded = encoded.replace(old, new)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest().upper()


def verify_payment_notification(params, hash_key, hash_iv):
    """
    驗證付款通知

    Args:
        params: 參數字典（來自 OMG 金流 POST）
        hash_key: Hash Key
        hash_iv: Hash IV

    Returns:
        tuple: (is_valid, status_message)

    Raises:
        Exception: CheckMacValue 不匹配時拋出
    """
    # 計算預期的 CheckMacValue
    calculated_mac = generate_check_mac_value(params, hash_key, hash_iv)
    server_mac = params.get("CheckMacValue", "").upper()

    # 比對簽名
    if calculated_mac != server_mac:
        error_msg = f"CheckMacValue 不匹配！\n計算值: {calculated_mac}\n服務器值: {server_mac}"
        raise Exception(error_msg)

    # 狀態檢查
    rtn_code = params.get("RtnCode", "")
    rtn_msg = params.get("RtnMsg", "")

    if rtn_code != "1":
        return False, f"支付失敗: {rtn_msg} (RtnCode: {rtn_code})"

    # 付款成功
    trade_no = params.get("TradeNo", "N/A")
    trade_amt = params.get("TradeAmt", "N/A")
    payment_date = params.get("PaymentDate", "N/A")

    return True, f"付款成功！\n交易編號: {trade_no}\n交易金額: {trade_amt} NT$\n付款時間: {payment_date}"


def parse_params_from_str(param_str):
    """從字串解析參數"""
    params = {}
    for item in param_str.split("&"):
        if "=" in item:
            key, value = item.split("=", 1)
            params[key] = value
    return params


def main():
    parser = argparse.ArgumentParser(
        description="驗證 OMG Payment 付款通知"
    )

    parser.add_argument(
        "--hash-key",
        type=str,
        default="265fIDjIvesceXWM",
        help="Hash Key"
    )
    parser.add_argument(
        "--hash-iv",
        type=str,
        default="pOOvhGd1V2pJbjfX",
        help="Hash IV"
    )
    parser.add_argument(
        "--payment-no",
        type=str,
        help="付款編號（用於輸出）"
    )

    args = parser.parse_args()

    # 從 stdin 讀取參數
    param_str = sys.stdin.read().strip()

    if not param_str:
        print("錯誤：未提供參數字串", file=sys.stderr)
        sys.exit(1)

    # 解析參數
    params = parse_params_from_str(param_str)

    # 簽名都在 stdout 輸出（可以做測試驗證）

    try:
        # 驗證
        is_valid, message = verify_payment_notification(params, args.hash_key, args.hash_iv)

        print("=" * 80)
        if args.payment_no:
            print(f"付款通知驗證結果：{args.payment_no}")
        else:
            print("付款通知驗證結果")
        print("=" * 80)

        # 顯示參數摘要
        print("\n參數摘要：")
        print("-" * 80)
        for k, v in list(params.items())[:10]:  # 只顯示前 10 個
            key_display = k if k != "CheckMacValue" else "CheckMacValue (驗證中...)"
            print(f"{key_display}: {v}")

        if "CheckMacValue" in params:
            print(f"\n服務器 CheckMacValue: {params['CheckMacValue']}")

        print("\n" + "=" *  cat末自:

        # 發送 1|OK（如果測試）

        if not is_valid:
            print(f"✗ 驗證失敗：{message}")
            sys.exit(1)
        else:
            print(f"✓ 驗證成功！")
            print(f"\n{message}")
            print("\n（若要回應 OMG 金流，請發送: 1|OK）")
            sys.exit(0)

    except Exception as e:
        print("=" * 80)
        print("✗ 驗證失敗")
        print("=" * 80)
        print(f"\n{str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()