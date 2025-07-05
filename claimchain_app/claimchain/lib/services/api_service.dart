import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/cardiac_event.dart';

class ApiService {
  static const String _baseUrl =
      'https://your-backend-api.com'; // Replace with actual backend URL
  static const String _syncEndpoint = '/api/cardiac-events';

  Future<bool> syncCardiacEvent(CardiacEvent event) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl$_syncEndpoint'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode(event.toJson()),
      );

      return response.statusCode == 200 || response.statusCode == 201;
    } catch (e) {
      print('Error syncing cardiac event: $e');
      return false;
    }
  }
}
