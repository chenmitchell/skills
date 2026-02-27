#!/usr/bin/env python3
"""
OMG Payment - CheckMacValue 生成工具

使用方法：
    python3 generate_check_mac_value.py <merchant_trade_no> <total_amount> [other_params...]

範例：
    python3 generate_check_mac_value.py "ORDER123456" 299

完整參數範例：
    python3 generate_check_mac_value.py "ORDER20260227001" 299 --merchant-id "1000031" \
        --hash-key "265fIDjIvesceXWM" --hash-iv "pOOvhGd1V2pJbjfX" \
        --trade-desc "測試訂單" --item-name "測試商品"
"""

import hashlib
import argparse
import sys
import os
from datetime import datetime

# .NET URL Encoding 替換表格
DOTNET_REPLACEMENTS = {
    "%2d": "-", "%5f": "_", "%2e": ".", "%21": "!", "%2a": "*", "%28": "(", "%29": ")",
}


def generate_check_mac_value(params, hash_key, hash_iv):
    """
    生成 OMG CheckMacValue（SHA256）

    Args:
        params: 參數字典（必須包含所有 Payment API 參數）
        hash_key: Hash Key
        hash_iv: Hash IV

    Returns:
        CheckMacValue 字串（大寫 SHA256）
    """
    # 排除 CheckMacValue，並篩選空值
    filtered = {k: v for k, v in params.items() if k != "CheckMacValue" and v}
    # 按鍵名排序（不區分大小寫）
    sorted_keys = sorted(filtered.keys(), key=lambda k: k.lower())
    # 組合參數字串
    param_str = "&".join(f"{k}={filtered[k]}" for k in sorted_keys)
    # 加上 HashKey 和 HashIV
    raw = f"{hash_key}&{param_str}&{hash_iv}"
    # URL encode
    encoded = quote(raw, safe="").lower()
    # .NET 特殊替換
    for old, new in DOTNET_REPLACEMENTS.items():
        encoded = encoded.replace(old, new)
    # SHA256 hash
    check_mac_value = hashlib.sha256(encoded.encode("utf-8")).hexdigest().upper()

    return check_mac_value


def parse_cli_args():
    """解析命令列參數"""
    parser = argparse.ArgumentParser(
        description="生成 OMG Payment CheckMacValue（SHA256）"
    )

    parser.add_argument("merchant_trade_no", help="訂單編號（MerchantTradeNo）")
    parser.add_argument("total_amount", type=int, help="訂單金額（TotalAmount）")

    # 選擇性參數
    parser.add_argument(
        "--merchant-id",
        type=str,
        default=os.getenv("OMG_MERCHANT_ID", "1000031"),
        help="商家 ID（MerchantID）"
    )
    parser.add_argument(
        "--hash-key",
        type=str,
        default=os.getenv("OMG_HASH_KEY", "265fIDjIvesceXWM"),
        help="Hash Key"
    )
    parser.add_argument(
        "--hash-iv",
        type=str,
        default=os.getenv("OMG_HASH_IV", "pOOvhGd1V2pJbjfX"),
        help="Hash IV"
    )
    parser.add_argument(
        "--trade-desc",
        type=str,
        default="Outpost News Service 测试订单",
        help="交易描述（TradeDesc）"
    )
    parser.add_argument(
        "--item-name",
        type=str,
        default="Outpost News Service 测试商品",
        help="項目名稱（ItemName）"
    )
    parser.add_argument(
        "--period-type",
        type=str,
        default="M",
        choices=["D", "M", "Y"],
        help="扣款週期（PeriodType）：D=每日, M=每月（預設）, Y=每年"
    )
    parser.add_argument(
        "--frequency",
        type=int,
        help="扣款次數（Frequency）：D=1-365, M=1-12, Y=1（視方案而定）"
    )
    parser.add_argument(
        "--exec-times",
        type=int,
        help="總執行次數（ExecTimes）：D=最多999, M=最多99, Y=最多9（視方案而定）"
    )
    parser.add_argument(
        "--return-url",
        type=str,
        help="ReturnURL（第一次付款回應）"
    )
    parser.add_argument(
        "--period-return-url",
        type=str,
        help="PeriodReturnURL（第2筆後每次付款回應）"
    )
    parser.add_argument(
        "--production",
        type=lambda x: x.lower() == "true",
        default=True,
        help="生產環境：true=生產環境, false=測試環境"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="1.0.0"
    )

    args = parser.parse_args()

    # 計算隨機性 ease...
    if args.frequency is None or args.exec_times is None:
        if args.period_type == "M":
            args.frequency = 4
            args.exec_times = 4
        else:
            args.frequency = 12
            args.exec_times = 12

    return args


def main():
    """主程式"""
    args = parse_cli_args()

    # 構建參數
    params = {
        "MerchantID": args.merchant_id,
        "MerchantTradeNo": args.merchant_trade_no,
        "MerchantTradeDate": datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
        "PaymentType": "aio",
        "TotalAmount": args.total_amount,
        "TradeDesc": args.trade_desc,
        "ItemName": args.item_name,
        "ChoosePayment": "Credit",
        "PeriodType": args.period_type,
        "Frequency": args.frequency,
        "ExecTimes": args.exec_times,
    }

    # 添加回調 URL（如果提供）
    if args.return_url:
        params["ReturnURL"] = args.return_url
    if args.period_return_url:
        params["PeriodReturnURL"] = args.period_return_url

    # 生成 CheckMacValue
    check_mac_value = generate_check_mac_value(params, args.hash_key, args.hash_iv)

    # 輸出參數
    print("=" * 80)
    print("OMG Payment - 檢查參數生成結果")
    print("=" * 80)
    print(f"MerchantID: {params['MerchantID']}")
    print(f"MerchantTradeNo: {params['MerchantTradeNo']}")
    print(f"MerchantTradeDate: {params['MerchantTradeDate']}")
    print(f"PaymentType: {params['PaymentType']}")
    print(f"TotalAmount: {params['TotalAmount']}")
    print(f"TradeDesc: {params['TradeDesc']}")
    print(f"ItemName: {params['ItemName']}")
    print(f"ChoosePayment: {params['ChoosePayment']}")
    print(f"PeriodType: {params['PeriodType']}")
    print(f"Frequency: {params['Frequency']}")
    print(f"ExecTimes: {params['ExecTimes']}")
    if "ReturnURL" in params:
        print(f"ReturnURL: {params['ReturnURL']}")
    if "PeriodReturnURL" in params:
        print(f"PeriodReturnURL: {params['PeriodReturnURL']}")

    print(f"\nCheckMacValue (SHA256):")
    print("-" * 80)
    print(check_mac_value)

    print(f"\n完整 POST URL:")
    print("-" * 80)
    base_url = "https://payment.funpoint.com.tw" if args.production else "https://payment-stage.funpoint.com.tw"
    print(f"{base_url}/Cashier/AioCheckOut/V5")

    print(f"\n表單資料（已 URL encode）:")
    print("-" * 80)
    import urllib.parse
    form_data = urllib.parse.urlencode(params, doseq=True)
    print(form_data)

    print("=" * 80)
    return 0


if __name__ == "__main__":
    sys.exit(main())