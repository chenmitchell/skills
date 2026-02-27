---
name: omg-payment
description: OMG金流(AioCheckOut V5)定期定額支付整合。用於建立訂單、計算CheckMacValue(SHA256)、處理定期定額流程。包含環境變數參數(key/iv/merchantID)、參數驗證、錯誤處理、定期定額流程(ReturnURL & PeriodReturnURL)。當需要處理omg支付、建立定期定額訂單、計算SHA256簽名時使用。
---

# OMG Payment (FunPoint) - 茂為歐買尬數位科技股份有限公司

## 基本資訊

| 項目 |說明|
|------|------|
| **收款對象** | 茂為歐買尬數位科技股份有限公司（TWSE: 3687）|
| **API 版本** | AioCheckOut V5 |
| **環境** | 生產環境 `/Cashier/AioCheckOut/V5` | 測試環境 `https://payment-stage.funpoint.com.tw/Cashier/AioCheckOut/V5` |
| **傳輸方式** | HTTP POST (form-urlencoded) |
| **加密方式** | CheckMacValue (SHA256) |

---

## 環境變數設定

```bash
OMG_MERCHANT_ID=1000031          # 商家編號
OMG_HASH_KEY=265fIDjIvesceXWM   # Hash Key（用於計算 CheckMacValue）
OMG_HASH_IV=pOOvhGd1V2pJbjfX    # Hash IV（用於計算 CheckMacValue）
OMG_PRODUCTION=true             # true = 生產環境, false = 測試環境
```

---

## 環境變數參數說明

| 參數 | Type | 說明 |
|------|------|------|
| **OMG_MERCHANT_ID** | String (10) | 商家編號 |
| **OMG_HASH_KEY** | String | Hash Key（SHA256 驗證用）|
| **OMG_HASH_IV** | String | Hash IV（SHA256 驗證用）|
| **OMG_PRODUCTION** | Boolean | 環境切換：true=生產環境, false=測試環境 |

---

## API 認證

### CheckMacValue 計算（CRITICAL）

OMG 金流使用 SHA256 進行簽名驗證，必須正確計算：

#### 演算法步驟

1. 將所有參數（排除 CheckMacValue）按 Key 字母排序（A-Z，不區分大小寫）
2. 組合成 key=value 格式，用 & 分隔
3. 加上前綴 `HashKey=<key>&` 和後綴 `&HashIV=<iv>`
4. 對整個字串進行 URL encoding
5. 轉成小寫
6. 替換 .NET URL Encoding 特殊字元（見下表）
7. SHA256 hash
8. 轉成大寫

#### .NET URL Encoding 替換表格

必須執行此替換（不可忽略）：

| URL Encode | 替換為 |
|------------|--------|
| %2d | - |
| %5f | _ |
| %2e | . |
| %21 | ! |
| %2a | * |
| %28 | ( |
| %29 | ) |

---

## Python 實作範例

### 1. CheckMacValue 生成函式

```python
import hashlib
from urllib.parse import quote

DOTNET_REPLACEMENTS = {
    "%2d": "-", "%5f": "_", "%2e": ".", "%21": "!", "%2a": "*", "%28": "(", "%29": ")",
}

def generate_check_mac_value(params, hash_key, hash_iv):
    """生成 OMG CheckMacValue（SHA256）"""
    # 排除 CheckMacValue，並篩選空值
    filtered = {k: v for k, v in params.items() if k != "CheckMacValue" and v}
    # 按鍵名排序
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
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest().upper()
```

### 2. 建立定期定額訂單表單

```python
import urllib.parse
from datetime import datetime

def create_recurring_order_params(
    merchant_trade_no,
    period_amount,
    period_type="M",
    frequency=4,
    exec_times=4,
    description="Outpost-News-Monitoring",
    item_name="Outpost News Service",
    return_url=None,
    period_return_url=None,
    hash_key=None,
    hash_iv=None,
    merchant_id=None,
    production=True
):
    """建立定期定額訂單參數"""
    # 判斷 API URL
    base_url = "https://payment.funpoint.com.tw" if production else "https://payment-stage.funpoint.com.tw"

    # 構建參數
    params = {
        "MerchantID": merchant_id,
        "MerchantTradeNo": merchant_trade_no,
        "MerchantTradeDate": datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
        "PaymentType": "aio",
        "TotalAmount": period_amount,
        "TradeDesc": description[:200],
        "ItemName": item_name[:400],
        "ChoosePayment": "Credit",  # 定期定額必須選 Credit
        "PeriodType": period_type,
        "Frequency": frequency,
        "ExecTimes": exec_times,
    }

    # 添加回調 URL
    if return_url:
        params["ReturnURL"] = return_url
    if period_return_url:
        params["PeriodReturnURL"] = period_return_url

    # 計算 CheckMacValue
    params["CheckMacValue"] = generate_check_mac_value(params, hash_key, hash_iv)

    return {
        "url": f"{base_url}/Cashier/AioCheckOut/V5",
        "data": urllib.parse.urlencode(params, doseq=True),
        "method": "POST",
        "headers": {"Content-Type": "application/x-www-form-urlencoded"}
    }
```

### 3. 處理回調通知

定期定額每次扣款完成後，OMG 金流會 POST 到通知 URL（ReturnURL 或 PeriodReturnURL）：

| 參數 | 說明 |
|------|------|
| MerchantID | 商家 ID |
| MerchantTradeNo | 訂單編號 |
| RtnCode | 狀態：1 = 成功 |
| RtnMsg | 狀態訊息 |
| TradeNo | OMG 交易編號 |
| TradeAmt | 交易金額 |
| PaymentDate | 付款時間 |
| CheckMacValue | 必須驗證 |

**CRITICAL：** 必須以純文字回應 `1|OK` 給 OMG 金流，否則會重複通知。

```python
def verify_payment_notification(params, hash_key, hash_iv):
    """驗證付款通知"""
    # 排除 CheckMacValue 後重新計算
    calculated_mac = generate_check_mac_value(params, hash_key, hash_iv)
    server_mac = params.get("CheckMacValue", "").upper()

    # 比對簽名
    if calculated_mac != server_mac:
        raise ValueError(f"CheckMacValue 不匹配！計算值: {calculated_mac}, 服務器值: {server_mac}")

    # 狀態檢查
    if params.get("RtnCode") != "1":
        raise ValueError(f"支付失敗: {params.get('RtnMsg')}")

    return True
```

### 4. 發送 1|OK 回應

```python
@app.route('/payment/return', methods=['POST'])
def payment_return():
    """OMG 金流付款回應"""
    params = request.form.to_dict()
    verify_payment_notification(params, hash_key, hash_iv)

    # 保存付款資訊到資料庫
    save_payment_record(params)

    # 必須回應 1|OK
    return "1|OK", 200
```

---

## 定期定額流程

### 完整流程圖

```
用戶選擇訂閱方案
    ↓
建立訂單（計算 CheckMacValue）
    ↓
POST 到 OMG 金流頁面，選擇信用卡
    ↓
用戶授權「定期定額」
    ↓
第一次付款結果 → ReturnURL
    ↓
第 2 次及之後每個週期付款結果 → PeriodReturnURL
    ↓
商家回應 "1|OK"
```

### 關鍵點

- **ChoosePayment** 必須為 `Credit`
- **TotalAmount** 應等於 **PeriodAmount**
- **第一筆** 結果 POST 到 **ReturnURL**
- **第 2 筆後** 結果 POST 到 **PeriodReturnURL**（必須不同）
- **必須回應** `1|OK` 給每次通知

---

## 常見錯誤

### 1. CheckMacValue 計算錯誤

**原因：**
- 排序錯誤（非字母順序）
- HashKey/HashIV 位置錯誤
- 忽略 .NET 特殊替換
- 未轉大寫

**解決方法：**
- 確認參數已排除 CheckMacValue
- 確認 HashKey/HashIV 位置正確（前後各 1 個 &）
- 執行 .NET 替換表格
- 最終結果轉大寫

### 2. 專案重複

**原因：**
- MerchantTradeNo 未唯一

**解決方法：**
- 使用額外的 UUID 或時間戳記
- MerchantTradeNo 最多 20 字元

### 3. 無通知

**原因：**
- ReturnURL 未公開
- 未回應 `1|OK`

**解決方法：**
- 確認回傳 URL 可公開存取
- 每次通知皆回應 `1|OK`

### 4. 無第 2 筆確認

**原因：**
- PeriodReturnURL 未設定或與 ReturnURL 相同

**解決方法：**
- 確認 PeriodReturnURL 已設定且不同於 ReturnURL

---

## 測試參數（測試環境）

| 項目 | 值 |
|------|------|
| MerchantID | 1000031 |
| HashKey | 265fIDjIvesceXWM |
| HashIV | pOOvhGd1V2pJbjfX |
| 測試信用卡 | 4311-9522-2222-2222 |
| CVV | 222 |
| Expiry | 未來日期 |
| 測試 Card | 4311-9522-2222-2222 |

---

## 關閉定期定額

| 環境 | URL |
|------|-----|
| 生產 | https://payment.funpoint.com.tw/Cashier/CreditCardPeriodAction |
| 測試 | https://payment-stage.funpoint.com.tw/Cashier/CreditCardPeriodAction |

**參數：** MerchantID, MerchantTradeNo, Action=Cancel, CheckMacValue

---

## scripts/ 資源

包含可執行的 Python script，方便快速使用：

- `generate_check_mac_value.py` - CheckMacValue 生成工具
- `create_recurring_order.py` - 返回表單資料的工具函式
- `verify_payment.py` - 驗證付款通知的工具

---

## 安全提醒

- ✅ 信用卡資訊由 OMG 金流平台保管，商家不可見實際卡號
- ✅ HashKey/HashIV 應妥善保管，不得硬編碼
- ✅ 必須驗證所有通知的 CheckMacValue
- ✅ 所有金流操作應有交易記錄
- ✅ 測試環境與生產環境應嚴格切換
- ✅ 密碼需透過 HTTPS 傳輸

---

**最後更新：** 2026-02-27
**版本：** 1.0