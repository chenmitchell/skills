# OMG Payment 參考手冊（OMG Web Payment Gateway）

## 基本資訊

**金流供應商**: 法商 MacroWell OMG Digital Entertainment Co., Ltd.（OMG）

**技術版本**: AioCheckOut V5

**聯絡資訊**: https://www.funpoint.com.tw/

---

## 1. 環境設定

### 測試環境

| 項目 | 值 |
|------|------|
| API URL | https://payment-stage.funpoint.com.tw/Cashier/AioCheckOut/V5 |
| MerchantID | 1000031 |
| HashKey | 265fIDjIvesceXWM |
| HashIV | pOOvhGd1V2pJbjfX |

### 生產環境

| 項目 | 值 |
|------|------|
| API URL | https://payment.funpoint.com.tw/Cashier/AioCheckOut/V5 |
| MerchantID | （從 OMG 客服取得）|
| HashKey | （從 OMG 客服取得）|
| HashIV | （從 OMG 客服取得）|

### 環境變數

```bash
# 環境切換
OMG_PRODUCTION=false  # 測試環境（預設）
OMG_PRODUCTION=true   # 生產環境

# 很重要，不要硬編碼
OMG_MERCHANT_ID=1000031
OMG_HASH_KEY=265fIDjIvesceXWM
OMG_HASH_IV=pOOvhGd1V2pJbjfX
```

---

## 2. CheckMacValue 計算標準

### 演算法定義

```
1. 將所有參數排除 CheckMacValue，並篩選空值
2. 按鍵名字母順序排列（A-Z，不區分大小寫）
3. 組合成 key=value 格式，用 & 分隔
4. 加上前綴 HashKey=<key>& 和後綴 &HashIV=<iv>
5. 對整個字串執行 URL encoding
6. 轉成小寫
7. 替換 .NET URL Encoding 特殊字元（見替換表）
8. SHA256 hash
9. 轉成大寫
```

### .NET URL Encoding 替換表格

| URL Encode | 替換為 |
|------------|--------|
| %2d | - |
| %5f | _ |
| %2e | . |
| %21 | ! |
| %2a | * |
| %28 | ( |
| %29 | ) |

**重要：** 此替換是強制的，不可忽略！

### Python 實作

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
```

---

## 3. API 參數完整清單

### 基礎參數

| 參數 | Type | Max | 必填 | 說明 |
|------|------|-----|------|------|
| MerchantID | String | 10 | ✅ | 商家編號 |
| MerchantTradeNo | String | 20 | ✅ | 訂單編號（唯一） |
| MerchantTradeDate | String | 20 | ✅ | 結帳日期（yyyy/MM/dd HH:MM:SS） |
| PaymentType | String | 20 | ✅ | 固定值：aio |
| TotalAmount | Int | - | ✅ | 交易金額（NT$）|
| TradeDesc | String | 200 | ✅ | 交易描述 |
| ItemName | String | 400 | ✅ | 項目名稱（用 # 分隔） |
| ChoosePayment | String | 20 | ✅ | 付款方式：Credit, ATM, CVS, ALL |
| CheckMacValue | String | 64 | ✅ | SHA256 簽名 |
| EncryptType | Int | 1 | ✅ | 固定值：1（SHA256）|

### 定期定額參數

| 參數 | Type | 說明 | 限制 |
|------|------|------|------|
| PeriodAmount | Int | 每期金額 | 可寫續總和 |
| PeriodType | String | 扣款週期 | D=每日, M=每月, Y=每年 |
| Frequency | Int | 扣款次數 | D:1-365, M:1-12, Y:1 |
| ExecTimes | Int | 總執行次數 | D:最多999, M:最多99, Y:最多9 |
| PeriodReturnURL | String | 第2筆後付款回應 | 必須設（與 ReturnURL 不同）|

**注意：** 定期定額必須設為 `ChoosePayment: Credit`。

---

## 4. 定期定額流程

### 完整流程圖

```
用戶訂閱
    ↓
建立訂單（MerchantTradeNo）
    ↓
計算 CheckMacValue 加密簽名
    ↓
POST 到 OMG 金流頁面
    ↓
用戶選擇信用卡並授權「定期定額」
    ↓
第一次付款完成 → POST 到 ReturnURL
    ↓
商家記錄付款成功，回應 "1|OK"
    ↓
第 2 次及之後每個週期付款完成
    ↓
POST 到 PeriodReturnURL（不同於 ReturnURL）
    ↓
商家記錄並回應 "1|OK"
```

### 關鍵時剪

| 時刻 | URL | 參數 | 商家行動 |
|------|-----|------|----------|
| **訂單建立時** | /Cashier/AioCheckOut/V5 | CheckMacValue 已算 | POST 表單到 OMG |
| **第一次扣款** | ReturnURL | RtnCode=1, RtnMsg | 驗證簽名，回應 "1|OK" |
| **第2筆及之後** | PeriodReturnURL | RtnCode=1, RtnMsg | 驗證簽名，回應 "1|OK" |

---

## 5. 付款通知參數

### 通知參數（POST 到 ReturnURL/PeriodReturnURL）

| 參數 | 說明 |
|------|------|
| MerchantID | 商家 ID |
| MerchantTradeNo | 訂單編號 |
| RtnCode | 狀態：1 = 成功，其他 = 失敗 |
| RtnMsg | 狀態訊息 |
| TradeNo | OMG 交易編號 |
| TradeAmt | 交易金額 |
| PaymentDate | 付款時間（yyyy/MM/dd HH:MM:SS）|
| CheckMacValue | 必須驗證簽名 |

### 商家回應

**必須回應：**

```
1|OK
```

**錯誤處理：**
- 若回應非 `1|OK`，OMG 金流會重複通知
- 視為伺服器問題，應當重試回應

---

## 6. 取消定期定額

### API URL

| 環境 | URL |
|------|-----|
| 生產 | https://payment.funpoint.com.tw/Cashier/CreditCardPeriodAction |
| 測試 | https://payment-stage.funpoint.com.tw/Cashier/CreditCardPeriodAction |

### 參數

| 參數 | 說明 | Type |
|------|------|------|
| MerchantID | 商家 ID | String |
| MerchantTradeNo | 訂單編號 | String |
| Action | 動作：Cancel | String |
| CheckMacValue | SHA256 簽名 | String |

---

## 7. 常見錯誤處理

### CheckMacValue 401 錯誤

**錯誤訊息示例：**
```
- 查參數排序錯誤（非字母順序）
- HashKey/HashIV 位置錯誤（缺少 &）
- 未執行 .NET URL Encode 替換
- SHA256 未轉大寫
```

**解決方法：**
1. 使用完整的參數字典進行排序
2. 確認 HashKey 前後各有 `&`
3. 手動執行替換表格
4. 最終結果轉大寫

### 重複訂單

**錯誤訊息：**
```
MerchantTradeNo 重複
```

**解決方法：**
- 使用額外的時間戳或 UUID 確保唯一性
- MerchantTradeNo 最多 20 字元

### 無通知處理

**可能原因：**
- ReturnURL 未公開
- 未回應 `1|OK`

**解決方法：**
- 使用 HTTPS 回調 URL
- 每次通知都回應 `1|OK`

### 第 2 筆無法抵消

**可能原因：**
- PeriodReturnURL 未設或與 ReturnURL 相同

**解決方法：**
- 建立兩度不同的通知 URL
- 兩數需完全相同（完全不同 URL）

---

## 8. 安全建議

### ✅ 必須做到

- 使用 HTTPS 傳輸所有資料
- 妥善保管 HashKey/HashIV，不得硬編碼
- 每次付款都驗證 CheckMacValue
- 記錄所有交易
- 測試環境與生產環境嚴格切換

### ✅ 不應做的事

- 不得在代碼中硬編碼 HashKey/HashIV
- 不得存儲任何完整卡片資訊
- 不得跳過簽名驗證步驟
- 不得提供測試環境 URL 可在生產環境公開

### ✅ 當安全

- 信用卡資訊由 OMG 金流平台保管
- 商家不可見實際卡號
- 所有金流操作須有歷史記錄
- 建議導出月度報表備查

---

## 9. 測試用信用卡資訊

| 項目 | 值 |
|------|------|
| 測試信用卡 | 4311-9522-2222-2222 |
| CVV | 222 |
| 有效期 | 未來日期 |
| 驗證狀態 | 測試環境可用 |

---

## 10. 聯絡 OMG 金流

**官方網站:** https://www.funpoint.com.tw/

**客服專線**：（需從 OMG 官方確認）

**郵件聯絡**：（需從 OMG 官方確認）

---

## 11. 版本資訊

**參考版本：** 年月24-12 月

**參考時間：** 2026-02-27

**參考日期：** 2026-02-26

**功能狀態：** ✓ 核心功能已驗證

---

**最後更新：** 2026-02-27
**版本：** 1.1
**作者：** Mitch

**備註：** 本參考手冊基於 OMG Web Payment Gateway (AioCheckOut V5) 官方文檔整理，主要用於 AI 的程式碼生成與整合。實際操作前請務必與 OMG 金流客服確認最新規格。