import { parseAnaPayEmail, parseRakutenPayEmail, ParsedTransaction } from '../../src/mastra/tools/parser'; // Adjust path if needed

describe('Email Parsers', () => {
  describe('parseAnaPayEmail', () => {
    it('should correctly parse a valid ANA Pay email', () => {
      const sampleEmailBody = `
xxx 様


以下ご利用料金の決済が完了しました。

ご利用日時：2025-03-29 14:05:52
ご利用金額：8,250円
ご利用店舗：yyy

詳細はお使いのアプリからご確認いただけます。

＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿

■本メールは送信専用のため、こちらのメールアドレスにご返信いただいても
   対応はいたしかねますのでご了承ください。

万が一、当メールの内容にお心当たりがない場合は以下をご確認ください。
https://faq.ana-x.co.jp/faq/anapay/web/knowledge711.html

ANA Payに関するよくあるご質問は以下をご確認ください。
https://faq.ana-x.co.jp/faq/anapay/web/index.html


＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿
`;

      const expected: ParsedTransaction = {
        // Note: Month is 0-indexed in JS Date (0 = January, 2 = March)
        transactionDate: new Date(2025, 2, 29, 14, 5, 52),
        amount: 8250,
        currency: 'JPY',
        storeName: 'yyy',
        source: 'ANA Pay',
      };

      const result = parseAnaPayEmail(sampleEmailBody);

      // Expect result not to be null
      expect(result).not.toBeNull();

      // Compare date parts individually or use toISOString for reliable comparison
      expect(result?.transactionDate.getFullYear()).toEqual(expected.transactionDate.getFullYear());
      expect(result?.transactionDate.getMonth()).toEqual(expected.transactionDate.getMonth());
      expect(result?.transactionDate.getDate()).toEqual(expected.transactionDate.getDate());
      expect(result?.transactionDate.getHours()).toEqual(expected.transactionDate.getHours());
      expect(result?.transactionDate.getMinutes()).toEqual(expected.transactionDate.getMinutes());
      expect(result?.transactionDate.getSeconds()).toEqual(expected.transactionDate.getSeconds());

      // Compare other fields
      expect(result?.amount).toEqual(expected.amount);
      expect(result?.currency).toEqual(expected.currency);
      expect(result?.storeName).toEqual(expected.storeName);
      expect(result?.source).toEqual(expected.source);
    });

    it('should return null for an email body missing required fields', () => {
      const invalidEmailBody = `
xxx 様

ご利用ありがとうございます。

ご利用日時：2025-03-30 10:00:00
// Missing amount and store
`;
      const result = parseAnaPayEmail(invalidEmailBody);
      expect(result).toBeNull();
    });

    it('should return null for completely unrelated email content', () => {
      const unrelatedEmailBody = 'This is a completely different email.';
      const result = parseAnaPayEmail(unrelatedEmailBody);
      expect(result).toBeNull();
    });

    // TODO: Add more test cases for edge scenarios if necessary
    // (e.g., amount without comma, different store name formats if applicable)
  });

  describe('parseRakutenPayEmail', () => {
    it('should correctly parse a valid Rakuten Pay email', () => {
      const sampleEmailBody = `
ご利用明細


	
ご利用日時	2025/03/13(木) 14:52
伝票番号	PRD1979164-250313145221-566-0111

ご利用店舗	パティスリー　シェ・シシ
電話番号	092-791-3617

決済総額	¥6,770
ポイント	0
楽天キャッシュ	¥6,770
カード	¥0

獲得予定ポイント	100ポイント
楽天カードご利用分	-
楽天ペイご利用分	67ポイント
楽天キャッシュご利用分	33ポイント
※キャンペーン参加によるポイント進呈分は含まれません。
※ポイント進呈日に関しては、こちらをご覧ください。
お取引内容  決済
ご購入の商品やサービスに関するお問い合わせは、上記のご利用店舗宛に直接ご連絡ください。
お支払い日は、各カード会社が発行するご利用代金明細書でご確認ください。
事前分割設定を申請された場合は、お支払い回数が確定次第、楽天ペイアプリでお知らせします。
事前分割設定の詳細はこちら
`;
      const expected: Omit<ParsedTransaction, 'originalEmailBody'> = { // Use Omit if not checking originalEmailBody
        transactionDate: new Date(2025, 2, 13, 14, 52), // Month is 0-indexed
        amount: 6770,
        currency: 'JPY',
        storeName: 'パティスリー　シェ・シシ',
        source: 'Rakuten Pay',
      };

      const result = parseRakutenPayEmail(sampleEmailBody);
      expect(result).not.toBeNull();

      // Compare date parts
      expect(result?.transactionDate.getFullYear()).toEqual(expected.transactionDate.getFullYear());
      expect(result?.transactionDate.getMonth()).toEqual(expected.transactionDate.getMonth());
      expect(result?.transactionDate.getDate()).toEqual(expected.transactionDate.getDate());
      expect(result?.transactionDate.getHours()).toEqual(expected.transactionDate.getHours());
      expect(result?.transactionDate.getMinutes()).toEqual(expected.transactionDate.getMinutes());

      // Compare other fields
      expect(result?.amount).toEqual(expected.amount);
      expect(result?.currency).toEqual(expected.currency);
      expect(result?.storeName).toEqual(expected.storeName);
      expect(result?.source).toEqual(expected.source);
    });

    it('should return null if key information is missing', () => {
       const invalidEmailBody = `
ご利用明細
ご利用日時	2025/03/13(木) 14:52
ご利用店舗	Some Store
// Missing 決済総額
`;
       const result = parseRakutenPayEmail(invalidEmailBody);
       expect(result).toBeNull();
    });
     it('should return null for completely unrelated email content', () => {
      const unrelatedEmailBody = 'Another different email.';
      const result = parseRakutenPayEmail(unrelatedEmailBody);
      expect(result).toBeNull();
    });

    // TODO: Add tests for variations (e.g., different formatting, HTML entities if applicable)
  });
}); 