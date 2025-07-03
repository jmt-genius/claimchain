import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';
import '../models/cardiac_event.dart';

class DatabaseService {
  static Database? _database;

  Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await _initDatabase();
    return _database!;
  }

  Future<Database> _initDatabase() async {
    String path = join(await getDatabasesPath(), 'claimchain.db');
    return await openDatabase(path, version: 1, onCreate: _createDatabase);
  }

  Future<void> _createDatabase(Database db, int version) async {
    await db.execute('''
      CREATE TABLE cardiac_events(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customerId TEXT NOT NULL,
        timestamp INTEGER NOT NULL,
        heartRate INTEGER NOT NULL,
        mode TEXT NOT NULL,
        summary TEXT NOT NULL
      )
    ''');
  }

  Future<void> saveCardiacEvent(CardiacEvent event) async {
    final db = await database;

    // Delete previous events (keep only the most recent)
    await db.delete('cardiac_events');

    // Insert the new event
    await db.insert('cardiac_events', event.toMap());
  }

  Future<CardiacEvent?> getLatestCardiacEvent() async {
    final db = await database;
    final List<Map<String, dynamic>> maps = await db.query(
      'cardiac_events',
      orderBy: 'timestamp DESC',
      limit: 1,
    );

    if (maps.isNotEmpty) {
      return CardiacEvent.fromMap(maps.first);
    }
    return null;
  }

  Future<void> close() async {
    final db = await database;
    await db.close();
  }
}
