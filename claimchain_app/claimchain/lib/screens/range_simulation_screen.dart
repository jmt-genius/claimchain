import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/heart_rate_provider.dart';
import 'dart:async';

class RangeSimulationScreen extends StatefulWidget {
  const RangeSimulationScreen({super.key});

  @override
  State<RangeSimulationScreen> createState() => _RangeSimulationScreenState();
}

class _RangeSimulationScreenState extends State<RangeSimulationScreen> {
  final _formKey = GlobalKey<FormState>();
  int _minBpm = 98;
  int _maxBpm = 100;
  bool _isSimulating = false;
  Timer? _resetTimer;

  @override
  void initState() {
    super.initState();
    // Check if simulation is already running
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final provider = Provider.of<HeartRateProvider>(context, listen: false);
      setState(() {
        _isSimulating = provider.isRangeSimulation;
        if (_isSimulating) {
          _minBpm = provider.rangeMin;
          _maxBpm = provider.rangeMax;
        }
      });
    });
  }

  @override
  void dispose() {
    _resetTimer?.cancel();
    super.dispose();
  }

  void _onRangeChanged() {
    _resetTimer?.cancel();
    _resetTimer = Timer(const Duration(seconds: 2), () {
      if (_isSimulating) {
        Provider.of<HeartRateProvider>(
          context,
          listen: false,
        ).startRangeSimulation(_minBpm, _maxBpm);
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Range Simulation')),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Form(
          key: _formKey,
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Text(
                'Specify BPM Range',
                style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 24),
              Row(
                children: [
                  Expanded(
                    child: TextFormField(
                      initialValue: _minBpm.toString(),
                      decoration: const InputDecoration(
                        labelText: 'Min BPM',
                        border: OutlineInputBorder(),
                      ),
                      keyboardType: TextInputType.number,
                      validator: (value) {
                        final v = int.tryParse(value ?? '');
                        if (v == null || v < 30) return 'Enter valid BPM';
                        return null;
                      },
                      onChanged: (value) {
                        final v = int.tryParse(value);
                        if (v != null && v < _maxBpm) {
                          setState(() => _minBpm = v);
                          _onRangeChanged();
                        }
                      },
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: TextFormField(
                      initialValue: _maxBpm.toString(),
                      decoration: const InputDecoration(
                        labelText: 'Max BPM',
                        border: OutlineInputBorder(),
                      ),
                      keyboardType: TextInputType.number,
                      validator: (value) {
                        final v = int.tryParse(value ?? '');
                        if (v == null || v < 30) return 'Enter valid BPM';
                        return null;
                      },
                      onChanged: (value) {
                        final v = int.tryParse(value);
                        if (v != null && v > _minBpm) {
                          setState(() => _maxBpm = v);
                          _onRangeChanged();
                        }
                      },
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 32),
              ElevatedButton(
                onPressed: _isSimulating
                    ? _stopSimulation
                    : () {
                        if (_formKey.currentState!.validate()) {
                          _formKey.currentState!.save();
                          setState(() => _isSimulating = true);
                          Provider.of<HeartRateProvider>(
                            context,
                            listen: false,
                          ).startRangeSimulation(_minBpm, _maxBpm);
                        }
                      },
                style: ElevatedButton.styleFrom(
                  backgroundColor: _isSimulating ? Colors.red : Colors.green,
                  padding: const EdgeInsets.symmetric(
                    vertical: 16,
                    horizontal: 32,
                  ),
                ),
                child: Text(
                  _isSimulating ? 'Stop Simulation' : 'Start Simulation',
                ),
              ),
              const SizedBox(height: 24),
              if (_isSimulating)
                const Text(
                  'Simulating heart rate in specified range...\nNo cardiac events will be triggered.',
                  style: TextStyle(color: Colors.grey),
                  textAlign: TextAlign.center,
                ),
            ],
          ),
        ),
      ),
    );
  }

  void _stopSimulation() {
    Provider.of<HeartRateProvider>(
      context,
      listen: false,
    ).stopRangeSimulation();
    setState(() => _isSimulating = false);
  }
}
