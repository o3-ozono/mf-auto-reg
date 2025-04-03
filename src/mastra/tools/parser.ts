/**
 * Represents the structured data extracted from a payment notification email.
 */
export interface ParsedTransaction {
  transactionDate: Date;
  amount: number;
  currency: string; // e.g., 'JPY'
  storeName: string;
  source: 'ANA Pay' | 'Rakuten Pay';
  originalEmailBody?: string; // Optional: for debugging/reference
}

/**
 * Helper function to create a ParsedTransaction object from extracted strings.
 * Performs validation and conversion.
 */
function createParsedTransaction(
  dateString: string, // Format depends on source
  amountString: string,
  storeString: string,
  source: 'ANA Pay' | 'Rakuten Pay'
): ParsedTransaction | null {
  try {
    let transactionDate: Date;
    if (source === 'ANA Pay') {
      // Expects 'YYYY-MM-DD HH:MM:SS'
      transactionDate = new Date(dateString.replace(/-/g, '/'));
    } else { // Rakuten Pay
      // Expects 'YYYY/MM/DD HH:MM'
      transactionDate = new Date(dateString);
    }

    const amount = parseInt(amountString.replace(/,/g, ''), 10);
    const storeName = storeString.trim();
    const currency = 'JPY'; // Both are JPY based for now

    // Validate parsed data
    if (isNaN(transactionDate.getTime()) || isNaN(amount) || !storeName) {
      console.error(`Failed to parse extracted values for ${source}. Date: ${dateString}, Amount: ${amountString}, Store: ${storeString}`);
      return null;
    }

    return {
      transactionDate,
      amount,
      currency,
      storeName,
      source,
    };
  } catch (error) {
    console.error(`Error processing extracted values for ${source}:`, error);
    return null;
  }
}

/**
 * Parses the body of an ANA Pay notification email to extract transaction details.
 *
 * @param emailBody The raw text content of the email body.
 * @returns A ParsedTransaction object if successful, null otherwise.
 */
export function parseAnaPayEmail(emailBody: string): ParsedTransaction | null {
  console.log('Attempting to parse ANA Pay email...');

  const dateTimeRegex = /ご利用日時：(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2})/;
  const amountRegex = /ご利用金額：([\d,]+)円/;
  const storeRegex = /ご利用店舗：(.+)/;

  const dateTimeMatch = emailBody.match(dateTimeRegex);
  const amountMatch = emailBody.match(amountRegex);
  const storeMatch = emailBody.match(storeRegex);

  if (dateTimeMatch?.[1] && amountMatch?.[1] && storeMatch?.[1]) {
    const result = createParsedTransaction(
      dateTimeMatch[1],
      amountMatch[1],
      storeMatch[1],
      'ANA Pay'
    );
    if (result) {
        console.log('Successfully parsed ANA Pay email.');
    }
    return result;
  } else {
    console.warn('Could not find all required fields in ANA Pay email body.');
    if (!dateTimeMatch) console.warn(' - DateTime not found');
    if (!amountMatch) console.warn(' - Amount not found');
    if (!storeMatch) console.warn(' - Store not found');
    return null;
  }
}

/**
 * Parses the body of a Rakuten Pay notification email to extract transaction details.
 *
 * @param emailBody The raw text content of the email body.
 * @returns A ParsedTransaction object if successful, null otherwise.
 */
export function parseRakutenPayEmail(emailBody: string): ParsedTransaction | null {
  console.log('Attempting to parse Rakuten Pay email...');

  const dateTimeRegex = /ご利用日時\s+(\d{4}\/\d{2}\/\d{2})\(\S\)\s(\d{2}:\d{2})/;
  const amountRegex = /決済総額\s+¥([\d,]+)/;
  const storeRegex = /ご利用店舗\s+([\s\S]+?)(?:\n|\r\n|\r)\s*電話番号/;

  const dateTimeMatch = emailBody.match(dateTimeRegex);
  const amountMatch = emailBody.match(amountRegex);
  const storeMatch = emailBody.match(storeRegex);

  // Note: Rakuten date needs combining date and time captures
  if (dateTimeMatch?.[1] && dateTimeMatch?.[2] && amountMatch?.[1] && storeMatch?.[1]) {
     const dateStr = `${dateTimeMatch[1]} ${dateTimeMatch[2]}`;
     const result = createParsedTransaction(
       dateStr, // Combined date and time
       amountMatch[1],
       storeMatch[1],
       'Rakuten Pay'
     );
     if (result) {
         console.log('Successfully parsed Rakuten Pay email.');
     }
     return result;
  } else {
    console.warn('Could not find all required fields in Rakuten Pay email body.');
     if (!dateTimeMatch) console.warn(' - DateTime not found');
     if (!amountMatch) console.warn(' - Amount not found');
     if (!storeMatch) console.warn(' - Store not found (check regex logic)');
    return null;
  }
}

// Removed the comment about exporting as Mastra tools for now, 
// as the focus is on the parsing logic itself.
