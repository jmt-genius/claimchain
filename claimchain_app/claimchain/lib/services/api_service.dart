import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/cardiac_event.dart';

class ApiService {
  static const String _baseUrl = 'http://10.10.209.71:8000';
  static const String _syncEndpoint = '/claims/cardiac-event';

  Future<bool> syncCardiacEvent(CardiacEvent event) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl$_syncEndpoint'),
        headers: {
          'Content-Type': 'application/json',
          'accept': 'application/json',
        },
        body: json.encode({
          'customerId': event.customerId,
          'bpm': event.heartRate,
          'timestamp': event.timestamp.toIso8601String(),
          'summary': event.summary,
        }),
      );

      print('Response: ${response.statusCode} ${response.body}');
      return response.statusCode == 200 || response.statusCode == 201;
    } catch (e) {
      print('Error syncing cardiac event: $e');
      return false;
    }
  }
}
