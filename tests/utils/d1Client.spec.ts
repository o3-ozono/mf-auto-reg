import { mock } from 'jest-mock-extended';
import type { D1Database, D1PreparedStatement, D1Result } from '@cloudflare/workers-types';
import { createD1Client, type D1Client, type NewTransactionData } from '../../src/lib/d1Client';

// Mock D1 objects using jest-mock-extended
const mockStatement = mock<D1PreparedStatement>();
const mockDb = mock<D1Database>();

// Reset mocks before each test to ensure isolation
beforeEach(() => {
  // Reset the mocks for D1PreparedStatement methods
  mockStatement.bind.mockClear();
  mockStatement.first.mockClear();
  mockStatement.run.mockClear();
  mockStatement.all.mockClear(); // Include .all() just in case

  // Reset the mock for D1Database method
  mockDb.prepare.mockClear();

  // Configure the mock chain for prepare -> bind -> statement
  mockStatement.bind.mockReturnValue(mockStatement); // statement.bind() should return the statement itself
  mockDb.prepare.mockReturnValue(mockStatement);     // db.prepare() should return the statement
});

describe('D1Client', () => {
  let d1Client: D1Client;

  // Create a new client instance before each test suite run, passing the mock DB
  beforeAll(() => {
    d1Client = createD1Client(mockDb);
  });

  // Test suite for checkDuplicate
  describe('checkDuplicate', () => {
    it('should return true if a record exists', async () => {
      // Arrange: Configure mockStatement.first() to return a non-null object (simulating record found)
      // The actual content doesn't matter for the null check
      mockStatement.first.mockResolvedValue({ '1': 1 });

      const sourceEmailId = 'existing-email-id';

      // Act: Call the function under test
      const result = await d1Client.checkDuplicate(sourceEmailId);

      // Assert: Verify the result and that the correct SQL was prepared and bound
      expect(result).toBe(true);
      expect(mockDb.prepare).toHaveBeenCalledWith('SELECT 1 FROM transactions WHERE source_email_id = ? LIMIT 1');
      expect(mockStatement.bind).toHaveBeenCalledWith(sourceEmailId);
      expect(mockStatement.first).toHaveBeenCalledTimes(1);
    });

    it('should return false if no record exists', async () => {
      // Arrange: Configure mockStatement.first() to return null (simulating record not found)
      mockStatement.first.mockResolvedValue(null);

      const sourceEmailId = 'non-existing-email-id';

      // Act
      const result = await d1Client.checkDuplicate(sourceEmailId);

      // Assert
      expect(result).toBe(false);
      expect(mockDb.prepare).toHaveBeenCalledWith('SELECT 1 FROM transactions WHERE source_email_id = ? LIMIT 1');
      expect(mockStatement.bind).toHaveBeenCalledWith(sourceEmailId);
      expect(mockStatement.first).toHaveBeenCalledTimes(1);
    });

    it('should throw an error if the database query fails', async () => {
       // Arrange: Configure mockStatement.first() to throw an error
      const dbError = new Error('Database connection error');
      mockStatement.first.mockRejectedValue(dbError);

      const sourceEmailId = 'any-email-id';

      // Act & Assert: Use expect().rejects.toThrow() for async errors
      await expect(d1Client.checkDuplicate(sourceEmailId))
        .rejects.toThrow('Failed to check duplicate transaction: Database connection error');

      // Verify prepare and bind were still called
      expect(mockDb.prepare).toHaveBeenCalledWith('SELECT 1 FROM transactions WHERE source_email_id = ? LIMIT 1');
      expect(mockStatement.bind).toHaveBeenCalledWith(sourceEmailId);
    });
  });

  // Test suite for registerTransaction
  describe('registerTransaction', () => {
    const testData: NewTransactionData = {
      source_email_id: 'new-email-id',
      parsed_data: { item: 'test', price: 100 },
    };
    const expectedParsedDataJson = JSON.stringify(testData.parsed_data);
    // Mock crypto.randomUUID before tests for this suite
    let randomUUIDSpy: jest.SpyInstance;

    beforeAll(() => {
      // Spy on crypto.randomUUID and mock its implementation
      // Return a string that matches the UUID format template literal type
      randomUUIDSpy = jest.spyOn(crypto, 'randomUUID').mockImplementation(() => '123e4567-e89b-12d3-a456-426614174000' as `${string}-${string}-${string}-${string}-${string}`);
    });

    afterAll(() => {
      // Restore the original implementation after tests
      randomUUIDSpy.mockRestore();
    });


    it('should register a new transaction and return its UUID', async () => {
      // Arrange: Configure mockStatement.run() to return success
      // Ensure the mock D1Result matches the expected type structure
      // Use type assertion for simplicity with minimal properties
      const mockSuccessResult = { success: true, meta: {} } as D1Result;
      mockStatement.run.mockResolvedValue(mockSuccessResult);

      // Act
      const result = await d1Client.registerTransaction(testData);

      // Assert
      expect(result).toBe('123e4567-e89b-12d3-a456-426614174000');
      expect(mockDb.prepare).toHaveBeenCalledWith('INSERT INTO transactions (id, source_email_id, parsed_data, mf_status) VALUES (?, ?, ?, ?)');
      expect(mockStatement.bind).toHaveBeenCalledWith(
        '123e4567-e89b-12d3-a456-426614174000',
        testData.source_email_id,
        expectedParsedDataJson,
        'pending' // Initial status
      );
      expect(mockStatement.run).toHaveBeenCalledTimes(1);
    });

     it('should throw specific error if run() throws UNIQUE constraint error', async () => {
      // Arrange: Configure mockStatement.run() to throw an error indicating UNIQUE constraint violation
      const dbError = new Error('D1_ERROR: UNIQUE constraint failed: transactions.source_email_id');
      mockStatement.run.mockRejectedValue(dbError);

      // Act & Assert
      await expect(d1Client.registerTransaction(testData))
        .rejects.toThrow(`Transaction with source_email_id '${testData.source_email_id}' already exists.`);

       // Verify prepare and bind were still called
       expect(mockDb.prepare).toHaveBeenCalledWith('INSERT INTO transactions (id, source_email_id, parsed_data, mf_status) VALUES (?, ?, ?, ?)');
       expect(mockStatement.bind).toHaveBeenCalledWith(
        '123e4567-e89b-12d3-a456-426614174000',
        testData.source_email_id,
        expectedParsedDataJson,
        'pending'
      );
    });

    it('should throw generic error for other database errors during run()', async () => {
      // Arrange: Configure mockStatement.run() to throw a generic error
      const dbError = new Error('Some other database error');
      mockStatement.run.mockRejectedValue(dbError);

      // Act & Assert
      await expect(d1Client.registerTransaction(testData))
        .rejects.toThrow(`Failed to register transaction: ${dbError.message}`);

       // Verify prepare and bind were still called
       expect(mockDb.prepare).toHaveBeenCalledWith('INSERT INTO transactions (id, source_email_id, parsed_data, mf_status) VALUES (?, ?, ?, ?)');
       expect(mockStatement.bind).toHaveBeenCalledWith(
        '123e4567-e89b-12d3-a456-426614174000',
        testData.source_email_id,
        expectedParsedDataJson,
        'pending'
      );
    });
  });

  // Test suite for updateTransactionStatus
  describe('updateTransactionStatus', () => {
    const transactionId = 'existing-uuid-67890';
    const newStatus = 'registered';

    it('should update the transaction status successfully', async () => {
      // Arrange: Configure mockStatement.run() for successful update
      const mockSuccessResult = { success: true, meta: { changes: 1 } } as D1Result; // Minimal success mock
      mockStatement.run.mockResolvedValue(mockSuccessResult);

      // Act
      await d1Client.updateTransactionStatus(transactionId, newStatus);

      // Assert
      expect(mockDb.prepare).toHaveBeenCalledWith('UPDATE transactions SET mf_status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?');
      expect(mockStatement.bind).toHaveBeenCalledWith(newStatus, transactionId);
      expect(mockStatement.run).toHaveBeenCalledTimes(1);
    });

    it('should throw error if transaction ID is not found (changes === 0)', async () => {
      // Arrange: Configure mockStatement.run() for success but 0 changes
      const mockNotFoundResult = { success: true, meta: { changes: 0 } } as D1Result;
      mockStatement.run.mockResolvedValue(mockNotFoundResult);

      // Act & Assert
      await expect(d1Client.updateTransactionStatus(transactionId, newStatus))
        .rejects.toThrow(`Transaction with ID '${transactionId}' not found for status update.`);

      // Verify prepare and bind were still called
      expect(mockDb.prepare).toHaveBeenCalledWith('UPDATE transactions SET mf_status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?');
      expect(mockStatement.bind).toHaveBeenCalledWith(newStatus, transactionId);
    });

     it('should throw error if run() throws an exception', async () => {
      // Arrange: Configure mockStatement.run() to throw an error
      const dbError = new Error('Network timeout');
      mockStatement.run.mockRejectedValue(dbError);

      // Act & Assert
      await expect(d1Client.updateTransactionStatus(transactionId, newStatus))
        .rejects.toThrow(`Failed to update transaction status: ${dbError.message}`);

       // Verify prepare and bind were still called
       expect(mockDb.prepare).toHaveBeenCalledWith('UPDATE transactions SET mf_status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?');
       expect(mockStatement.bind).toHaveBeenCalledWith(newStatus, transactionId);
    });
  });
}); 