import { createTool } from '@mastra/core/tools';
import { z } from 'zod';
import {
  parseAnaPayEmail,
  parseRakutenPayEmail,
  // ParsedTransaction interface might not be strictly needed here
  // if we rely solely on the Zod schema for the output type
} from './parser';

// Zod Schema for the *successful* output structure
const ParsedTransactionSchema = z.object({
  transactionDate: z.date(),
  amount: z.number().int(),
  currency: z.string().length(3),
  storeName: z.string().min(1),
  source: z.union([z.literal('ANA Pay'), z.literal('Rakuten Pay')]),
});

// Zod Schema for the *combined* output (success or null)
const OutputSchema = z.union([ParsedTransactionSchema, z.null()]);
// Infer the TypeScript type from the combined output schema
type OutputType = z.infer<typeof OutputSchema>;

// Zod Schema for the input
const InputSchema = z.object({
    emailBody: z.string({ description: 'The raw text content of the email body.' }),
});
// Infer the TypeScript type from the input schema
type InputType = z.infer<typeof InputSchema>;

// Use the Zod schema objects directly as generics for the Tool class
export const anaPayParserTool = createTool({
  id: 'anaPayEmailParser',
  description: 'Parses the body of an ANA Pay notification email to extract transaction details.',
  inputSchema: InputSchema,
  execute: async ({ context }) => {
    const result = parseAnaPayEmail(context.emailBody);
    return result;
  },
});

export const rakutenPayParserTool = createTool({
  id: 'rakutenPayEmailParser',
  description: 'Parses the body of a Rakuten Pay notification email to extract transaction details.',
  inputSchema: InputSchema,
  execute: async ({ context }) => {
    const result = parseRakutenPayEmail(context.emailBody);
    return result;
  },
});

// Optional: Export all tools as a collection if preferred
export const parserTools = {
    anaPayParserTool,
    rakutenPayParserTool,
};
