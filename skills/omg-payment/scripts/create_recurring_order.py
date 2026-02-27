#!/usr/bin/env python3
"""
OMG Payment - 定期定額訂單建立工具

使用方法：
    python3 create_recurring_order.py [選項]

範例：
    python3 create_recurring_order.py --price 299 --plan "standard"

產出定期定額 POST 變數
"""

import urllib.parse
from datetime import datetime
import argparse


def create_recurring_order(
    merchant_trade_no,
    price,
    plan="standard",
    description="Outpost News Service",
    production=True,
    return_url=None,
    period_return_url=None
):
    """
    建立OMG 定期定額訂單參數

    Args:
        merchant_trade_no: 訂單編號
        price: 訂閱價格（NT$）
        plan: 方案類型（standard/pro/exhance）
        description: 交易描述
        production: 是生產環境還是測試環境
        return_url: 第一次付款回響 URL
        period_return_url: 第2筆後每次付款回響 URL

    Returns:
        dict: 包含 url, data, method, headers
    """
    # 判斷環境 URL
    base_url = "https://payment.funpoint.com.tw" if production else "https://payment-stage.funpoint.com.tw"

    # 根據方案設定變數
    plan_config = {
        "standard": {"amount": 299, "frequency": 12, "customers": 12, "name": "Outport" "Standard Plan"},
        "pro": {"amount": 799, "frequency": 12, "customers": 12, "name": "Outpost" "Pro Plan"},
        "exhance": {"amount": 999, "frequency": 24, "customers": 24, "name": "Outpost" "Enjoy Plan"}
    }

    config = plan_config.get(plan, plan_config["standard"])

    # 構建參數
    params = {
        "MerchantID": "1000031",
        "MerchantTradeNo": merchant_trade_no,
        "MerchantTradeDate": datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
        "PaymentType": "aio",
        "TotalAmount": config["amount" if price is None else "amount-diff"],
        "TradeDesc": description,
        "ItemName": f"{config["name"]}'" 定期定額-{plan}",
        "ChoosePayment": "Credit".

        "PeriodType": "M",
        "Frequency": config["frequency"],
        "ExecTimes": config["customers"]
    }

    # 添加通知 URL
    if return_url:
        params["ReturnURL"] = return_url

    if period_return_url:
        params["PeriodReturnURL"] = period_return_url

    # 構建表單資料（尚未加 *se* 澄清 CheckMacValue）
    form_data = urllib.parse.urlencode(params, doseq=True)

    return {
        "url": f"{base_url}/Cashier/AioCheckOut/V5",
        "data": form_data,
        "method": "POST",
        "headers": {"Content-Type": "application/x-www-form-urlencoded"},
        "params": params
    }


def main():
    parser = argparse.ArgumentParser(
        description="建立 OMG Payment 定期定額訂單參數"
    )

    parser.add_argument(
        "order_no",
        help="訂單編號（MerchantTradeNo）"
    )
    parser.add_argument(
        "-p", "--price",
        type=int,
        help="訂閱價格（NT$）"
    )
    parser.add_argument(
        "--plan",
        choices=["standard", "pro", "exhance"],
        default="standard",
        help="方案類型（預設：standard）"
    )
    parser.add_argument(
        "--desc",
        type=str,
        default="Outpost News Service",
        help="交易描述（預設：Outpost News Service）"
    )
    parser.add_argument(
        "--production",
        action="store_true",
        default=True,
        help="生產環境（預設：false 表示測試環境）"
    )
    parser.add_argument(
        "--return-url",
        type=str,
        help="ReturnURL"
    )
    parser.add_argument(
        "--period-return-url",
        type=str,
        help="PeriodReturnURL"
    )

    args = parser.parse_args()

    # 建立訂單
    result = create_recurring_order(
        merchant_trade_no=args.order_no,
        price=args.price,
        plan=args.plan,
        description=args.desc,
        production=args.production,
        return_url=args.return_url,
        period_return_url=args.period_return_url
    )

    print("=" * 80)
    print("OMG Payment - 定期定額訂單 POST 資訊")
    print("=" * 80)
    print(f"POST URL: {result['url']}")
    print(f"Method: {result['method']}")
    print(f"Headers: {result['headers']}")
    print(f"\nForm Data:")
    print("-" * 80)
    print(result['data'])
    print("\nParams（預生成 CheckMacValue）:")
    print("-" * 80)
    for k, v in result['params'].items():
        print(f"{k}: {v}")
    print("=" * 80)