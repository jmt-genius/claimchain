class CardiacEvent {
  final String customerId;
  final DateTime timestamp;
  final int heartRate;
  final String mode; // 'simulation' or 'live'
  final String summary;

  CardiacEvent({
    required this.customerId,
    required this.timestamp,
    required this.heartRate,
    required this.mode,
    required this.summary,
  });

  Map<String, dynamic> toJson() {
    return {
      'customerId': customerId,
      'bpm': heartRate,
      'timestamp': timestamp.toIso8601String(),
      'summary': summary,
    };
  }

  factory CardiacEvent.fromJson(Map<String, dynamic> json) {
    return CardiacEvent(
      customerId: json['customerId'],
      timestamp: DateTime.parse(json['timestamp']),
      heartRate: json['bpm'],
      mode: json['mode'] ?? 'unknown',
      summary: json['summary'],
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'customerId': customerId,
      'timestamp': timestamp.millisecondsSinceEpoch,
      'heartRate': heartRate,
      'mode': mode,
      'summary': summary,
    };
  }

  factory CardiacEvent.fromMap(Map<String, dynamic> map) {
    return CardiacEvent(
      customerId: map['customerId'],
      timestamp: DateTime.fromMillisecondsSinceEpoch(map['timestamp']),
      heartRate: map['heartRate'],
      mode: map['mode'],
      summary: map['summary'],
    );
  }
}
