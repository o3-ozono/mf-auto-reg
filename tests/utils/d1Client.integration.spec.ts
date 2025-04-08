import { execSync } from 'child_process';
import { resolve } from 'path';
import fs from 'fs/promises'; // Import fs promises API
import { Miniflare } from 'miniflare';
import type { D1Database } from '@cloudflare/workers-types'; // Import D1Database type directly
import { createD1Client, type D1Client, type NewTransactionData, type Env } from '../../src/lib/d1Client';

// --- Wrangler Helper ---
// Adjust path to wrangler and database name/binding as needed
// wrangler.toml is assumed to be in the project root
const WRANGLER_PATH = 'npx wrangler'; // Or specify the direct path if needed
const DATABASE_BINDING_NAME = process.env.TEST_D1_BINDING_NAME || 'DB'; // Match wrangler.toml binding
const DATABASE_NAME = process.env.TEST_D1_DATABASE_NAME || 'mf-auto-reg-test-db'; // Use env var or default test DB name
const SCHEMA_PATH = resolve(__dirname, '../../schema.sql'); // Path relative to this test file
// Define a specific path for the test database file
const TEST_DB_PATH = resolve(__dirname, `../../.wrangler/state/d1/${DATABASE_NAME}.sqlite`);
const TEST_DB_DIR = resolve(__dirname, '../../.wrangler/state/d1');

// Function to run wrangler commands synchronously
const runWrangler = (command: string): Buffer => {
  const fullCommand = `${WRANGLER_PATH} d1 execute ${DATABASE_NAME} --local --${command}`;
  console.log(`Running Wrangler command: ${fullCommand}`);
  try {
    // Use --database flag to specify the database name for wrangler d1 commands
    // Pass --local for local D1 operations
    return execSync(fullCommand, { stdio: 'pipe' });
  } catch (error: any) {
    console.error(`Error executing wrangler command: ${fullCommand}`);
    console.error('Stderr:', error.stderr?.toString());
    console.error('Stdout:', error.stdout?.toString());
    throw error; // Re-throw to fail the test setup
  }
};

// --- Test Setup ---
describe('D1Client Integration Tests (using Local D1 Emulator)', () => {
  let mf: Miniflare | undefined;
  let d1Client: D1Client;
  let testDb: D1Database;

  // Before all tests: Setup Miniflare and apply schema
  beforeAll(async () => {
    console.log('Setting up integration test environment...');

    // 1. Ensure the test DB directory exists and cleanup old DB file
    try {
        await fs.mkdir(TEST_DB_DIR, { recursive: true });
        await fs.unlink(TEST_DB_PATH); // Attempt to delete existing file
        console.log(`Cleaned up existing test database file (if any): ${TEST_DB_PATH}`);
    } catch (error: any) {
        // Ignore error if file doesn't exist, but log other errors
        if (error.code !== 'ENOENT') {
            console.warn(`Could not delete existing test DB file: ${error.message}`);
        }
    }

    // 2. Setup Miniflare, pointing d1Persist directly to our test file path
    mf = new Miniflare({
      modules: true,
      script: `export default { fetch: () => new Response(null, { status: 404 }) };`,
      d1Databases: {
        [DATABASE_BINDING_NAME]: DATABASE_NAME, // Binding name
      },
      // Persist directly to the specified file path
      d1Persist: TEST_DB_PATH,
    });

    // Get the D1 binding from Miniflare
    try {
        const env = await mf.getBindings<Env>();
        if (!env.DB) {
            throw new Error(`Failed to get D1 binding '${DATABASE_BINDING_NAME}' from Miniflare.`);
        }
        testDb = env.DB;
    } catch (e) {
        console.error("Failed to initialize Miniflare or get D1 binding:", e);
        await mf?.dispose(); // Clean up Miniflare instance if setup failed
        throw new Error("Integration test setup failed: Miniflare D1 binding error.");
    }

    // 3. Apply schema directly using the bound testDb from Miniflare, statement by statement
    try {
        console.log(`Applying schema from ${SCHEMA_PATH} directly via Miniflare DB binding...`);
        const schemaSqlRaw = await fs.readFile(SCHEMA_PATH, 'utf-8');
        // Remove comments and collapse to single line statements separated by ;
        const schemaSqlClean = schemaSqlRaw
            .split('\n') // Split into lines
            .map(line => line.replace(/--.*$/, '').trim()) // Remove comments and trim lines
            .filter(line => line.length > 0) // Remove empty lines
            .join(' '); // Join back with spaces (might not be strictly needed but safe)

        // Split potentially multiple statements just in case, though schema.sql is likely single DROP/CREATE
        const statements = schemaSqlClean.split(';')
            .map(s => s.trim())
            .filter(s => s.length > 0);

        console.log(`Executing ${statements.length} statements...`);
        for (const statement of statements) {
            console.log(`Executing: ${statement}`);
            await testDb.exec(statement + ';'); // Add semicolon back for execution
        }
        console.log('Schema applied successfully via Miniflare.');
    } catch (e) {
        console.error("Failed to apply schema via Miniflare:", e);
        await mf?.dispose();
        throw new Error("Integration test setup failed: Could not apply schema via Miniflare.");
    }

    // Create the D1Client instance
    d1Client = createD1Client(testDb);
    console.log('Integration test environment setup complete.');
  }, 60000);

  // Before each test: Clean the database tables
  beforeEach(async () => {
    console.log('Cleaning database tables for test isolation...');
    try {
      // Use the bound DB instance for cleaning to ensure it targets the correct test DB
       await testDb.exec('DELETE FROM transactions');
    } catch(e) {
        console.error("Error cleaning database tables:", e)
        // Applying schema again might be too aggressive here, just log and fail.
        throw new Error("Failed to clean database tables before test.");
    }
    console.log('Database tables cleaned.');
  });

  // After all tests: Dispose Miniflare
  afterAll(async () => {
    console.log('Tearing down integration test environment...');
    await mf?.dispose();
    // Optionally, delete the local .sqlite file here if desired
    // fs.unlinkSync(`.wrangler/v3/d1/${DATABASE_NAME}.sqlite`);
    console.log('Integration test environment torn down.');
  });

  // --- Test Cases ---
  test('d1Client can be created', () => {
      // Simple initial test to ensure setup works
      expect(d1Client).toBeDefined();
  });

  describe('checkDuplicate (Integration)', () => {
    const testEmailId = 'test-duplicate@example.com';
    const nonExistentEmailId = 'non-existent@example.com';

    // Helper to insert a dummy record for testing existence checks
    const insertTestRecord = async (emailId: string) => {
      await testDb.prepare('INSERT INTO transactions (id, source_email_id, parsed_data, mf_status) VALUES (?, ?, ?, ?)')
        .bind(crypto.randomUUID(), emailId, '{}', 'pending')
        .run();
    };

    it('should return false when the source_email_id does not exist', async () => {
      // Act: Check for an ID known not to be in the (cleaned) DB
      const result = await d1Client.checkDuplicate(nonExistentEmailId);

      // Assert: Expect false as no record should exist
      expect(result).toBe(false);
    });

    it('should return true when the source_email_id exists', async () => {
      // Arrange: Insert a record with the specific email ID first
      await insertTestRecord(testEmailId);

      // Act: Check for the ID we just inserted
      const result = await d1Client.checkDuplicate(testEmailId);

      // Assert: Expect true as the record exists
      expect(result).toBe(true);
    });

    // Note: Testing the specific error thrown on DB failure is harder in integration
    //       tests without intentionally breaking the DB connection. The unit tests cover
    //       error handling based on mocked DB responses. This integration test focuses
    //       on the successful path against the emulator.
  });

  describe('registerTransaction (Integration)', () => {
    const newTxData: NewTransactionData = {
      source_email_id: 'new-transaction@example.com',
      parsed_data: { product: 'Integration Test Item', amount: 1234 },
    };

    // Helper to fetch a transaction by source_email_id directly from the DB
    const findRecordBySourceEmailId = async (emailId: string) => {
        const statement = testDb.prepare('SELECT id, source_email_id, parsed_data, mf_status FROM transactions WHERE source_email_id = ?');
        return await statement.bind(emailId).first();
    };

    it('should insert a new transaction and return its UUID', async () => {
      // Act: Register the new transaction
      const newId = await d1Client.registerTransaction(newTxData);

      // Assert: Check the returned ID (should be a UUID string)
      expect(newId).toEqual(expect.stringMatching(/^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$/));

      // Assert: Verify the record in the database directly
      const record = await findRecordBySourceEmailId(newTxData.source_email_id);
      expect(record).toBeDefined();
      expect(record).toEqual({
        id: newId, // Check if the inserted ID matches the returned ID
        source_email_id: newTxData.source_email_id,
        parsed_data: JSON.stringify(newTxData.parsed_data), // Data should be stored as JSON string
        mf_status: 'pending', // Initial status should be pending
      });
    });

    it('should throw an error if source_email_id already exists (UNIQUE constraint)', async () => {
      // Arrange: Insert a record first
      await d1Client.registerTransaction(newTxData);

      // Act & Assert: Attempt to insert the same record again and expect specific error
      await expect(d1Client.registerTransaction(newTxData))
        .rejects
        .toThrow(`Transaction with source_email_id '${newTxData.source_email_id}' already exists.`);

       // Assert: Verify only one record exists in the DB
       const statement = testDb.prepare('SELECT COUNT(*) as count FROM transactions WHERE source_email_id = ?');
       const result = await statement.bind(newTxData.source_email_id).first<{count: number}>();
       expect(result?.count).toBe(1);
    });

    // Note: Testing other DB failure modes (like connection errors) is less practical here
    // than in unit tests with mocks. We focus on successful insertion and constraint violations.
  });

  describe('updateTransactionStatus (Integration)', () => {
    const initialTxData: NewTransactionData = {
      source_email_id: 'update-test@example.com',
      parsed_data: { status: 'initial' },
    };
    let insertedTxId: string; // Store the ID of the inserted record for tests

    // Helper to fetch a transaction by ID directly from the DB
    const findRecordById = async (id: string) => {
        const statement = testDb.prepare('SELECT id, mf_status, updated_at FROM transactions WHERE id = ?');
        return await statement.bind(id).first<{ id: string, mf_status: string, updated_at: string }>();
    };

    // Insert a record before each test in this suite
    beforeEach(async () => {
        insertedTxId = await d1Client.registerTransaction(initialTxData);
    });

    it('should update the mf_status and updated_at timestamp for an existing transaction', async () => {
      const newStatus = 'registered';
      // Arrange: Get the initial state
      const initialRecord = await findRecordById(insertedTxId);
      expect(initialRecord?.mf_status).toBe('pending');
      const initialUpdatedAt = initialRecord?.updated_at;
      expect(initialUpdatedAt).toBeDefined(); // Ensure initialUpdatedAt is defined

      // Act: Update the status
      await d1Client.updateTransactionStatus(insertedTxId, newStatus);

      // Assert: Verify the record in the database directly
      const updatedRecord = await findRecordById(insertedTxId);
      expect(updatedRecord).toBeDefined();
      expect(updatedRecord?.mf_status).toBe(newStatus);
      // Check that updated_at is greater than or equal to the initial timestamp
      expect(updatedRecord?.updated_at).toBeDefined(); // Ensure updatedRecord.updated_at is defined
      if (initialUpdatedAt && updatedRecord?.updated_at) {
        expect(new Date(updatedRecord.updated_at).getTime()).toBeGreaterThanOrEqual(new Date(initialUpdatedAt).getTime());
      }
      // Optional: Check if the timestamp format looks correct (ISO-like)
      expect(updatedRecord?.updated_at).toMatch(/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/); // D1 timestamp format
    });

    it('should throw an error if the transaction ID to update does not exist', async () => {
      const nonExistentId = crypto.randomUUID(); // Generate a random non-existent UUID
      const newStatus = 'error';

      // Act & Assert: Attempt to update a non-existent record
      await expect(d1Client.updateTransactionStatus(nonExistentId, newStatus))
        .rejects
        .toThrow(`Transaction with ID '${nonExistentId}' not found for status update.`);
    });

     it('should update the status correctly even if called multiple times', async () => {
        // Arrange: Update status to 'registered' first
        await d1Client.updateTransactionStatus(insertedTxId, 'registered');
        const recordAfterFirstUpdate = await findRecordById(insertedTxId);
        expect(recordAfterFirstUpdate?.mf_status).toBe('registered');
        const updatedAtAfterFirst = recordAfterFirstUpdate?.updated_at;
        expect(updatedAtAfterFirst).toBeDefined(); // Ensure updatedAtAfterFirst is defined

        // Ensure sufficient time passes for the timestamp to definitely change
        await new Promise(resolve => setTimeout(resolve, 1100)); // Increase delay to > 1 second

        // Act: Update status again to 'error'
        const secondStatus = 'error';
        await d1Client.updateTransactionStatus(insertedTxId, secondStatus);

        // Assert: Verify the final status and timestamp change
        const recordAfterSecondUpdate = await findRecordById(insertedTxId);
        expect(recordAfterSecondUpdate?.mf_status).toBe(secondStatus);
        expect(recordAfterSecondUpdate?.updated_at).toBeDefined(); // Ensure recordAfterSecondUpdate.updated_at is defined

        // Check that the second timestamp is strictly greater than the first updated timestamp
        if (updatedAtAfterFirst && recordAfterSecondUpdate?.updated_at) {
             expect(new Date(recordAfterSecondUpdate.updated_at).getTime()).toBeGreaterThan(new Date(updatedAtAfterFirst).getTime());
        }
    });
  });

}); 