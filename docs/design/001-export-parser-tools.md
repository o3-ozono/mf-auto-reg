# Design Doc 001: Export Email Parsers as Mastra Tools

**Date:** 2025-04-03 (Adjust as needed)
**Status:** Proposed

## 1. Context & Scope
The email parser functions (`parseAnaPayEmail`, `parseRakutenPayEmail`) have been implemented and tested (related to Issue #11 / PR #12). This task focuses on making these functions available as standard Mastra Tools so they can be easily integrated into Mastra Workflows or Agents.

## 2. Goals & Non-Goals
**Goals:**
- Define Mastra Tools that wrap the `parseAnaPayEmail` and `parseRakutenPayEmail` functions.
- Define input (string) and output (ParsedTransaction | null) schemas for the tools using Zod.
- Export the defined tools from `src/mastra/tools/index.ts`.

**Non-Goals:**
- Modifying the underlying parser logic.
- Integrating the tools into a workflow (this will be a separate task).
- Adding complex error handling beyond returning `null` (handled by the underlying functions).

## 3. Proposed Design
1. Create `src/mastra/tools/index.ts` if it doesn't exist.
2. Import `Tool` from `@mastra/core`, `z` from `zod`, and the parser functions/interface from `./parser`.
3. Define a Zod schema for the `ParsedTransaction` interface (or a simplified version for the output). Handling `Date` objects in Zod requires attention (e.g., using `z.date()` or `z.string().transform(...)`). Start with `z.date()`. The output schema must allow `null`.
4. Create `anaPayParserTool` using `new Tool({ ... })`:
   - `name`: `anaPayEmailParser`
   - `description`: "Parses ANA Pay email body to extract transaction details."
   - `inputSchema`: `z.object({ emailBody: z.string() })`
   - `outputSchema`: `z.union([ParsedTransactionSchema, z.null()])` (where `ParsedTransactionSchema` is the Zod schema for the output)
   - `execute`: Async function calling `parseAnaPayEmail(inputs.emailBody)`.
5. Create `rakutenPayParserTool` similarly.
6. Export both tools from `src/mastra/tools/index.ts`.

**Zod Schema for ParsedTransaction (Initial Draft):**
```typescript
const ParsedTransactionSchema = z.object({
  transactionDate: z.date(), // Or z.string().datetime() if preferred for transport
  amount: z.number().int(), // Assuming integer amounts based on examples
  currency: z.string().length(3), // Assuming 3-letter currency code like 'JPY'
  storeName: z.string().min(1), // Store name should not be empty
  source: z.union([z.literal('ANA Pay'), z.literal('Rakuten Pay')]),
  // originalEmailBody is optional and mainly for debugging, omit from schema
});
```
*(Schema refined slightly with `.int()`, `.length(3)`, `.min(1)` for better validation)*

## 4. Alternatives Considered (Optional)
- Combining both parsers into a single tool with a 'type' input: Decided against this for now to keep tools focused and simple.

## 5. Open Questions / Discussion Points
- Best way to handle `Date` type in Zod schema for tool output? (Stick with `z.date()` for now). 