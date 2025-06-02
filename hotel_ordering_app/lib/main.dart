import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:webview_flutter/webview_flutter.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Hotel Ordering',
      debugShowCheckedModeBanner: false, // hide DEBUG badge
      theme: ThemeData(
        primarySwatch: Colors.purple,
        scaffoldBackgroundColor: const Color(0xFFFFF5FF),
      ),
      home: const MenuWebViewPage(),
    );
  }
}

class MenuWebViewPage extends StatefulWidget {
  const MenuWebViewPage({super.key});
  @override
  State<MenuWebViewPage> createState() => _MenuWebViewPageState();
}

class _MenuWebViewPageState extends State<MenuWebViewPage> {
  late final WebViewController _controller;
  bool _isLoading = true;
  String _pageTitle = '';

  static const String emulatorUrl = 'http://10.0.2.2:8000/menu/';

  @override
  void initState() {
    super.initState();

    _controller =
        WebViewController()
          ..setJavaScriptMode(JavaScriptMode.unrestricted)
          ..setNavigationDelegate(
            NavigationDelegate(
              onPageStarted: (_) => setState(() => _isLoading = true),
              onPageFinished: (_) async {
                final title = await _controller.getTitle();
                setState(() {
                  _isLoading = false;
                  _pageTitle = title ?? '';
                });
              },
            ),
          )
          ..loadRequest(Uri.parse(emulatorUrl));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        // always show the real <title> from your Django page (or blank until it's loaded)
        title: Text(_pageTitle),
        elevation: 0,
        actions: [
          if (_isLoading)
            const Padding(
              padding: EdgeInsets.only(right: 16),
              child: Center(
                child: SizedBox(
                  width: 18,
                  height: 18,
                  child: CircularProgressIndicator(
                    color: Colors.white,
                    strokeWidth: 2,
                  ),
                ),
              ),
            ),
        ],
      ),
      body:
          kIsWeb
              ? const Center(child: Text('WebView is only supported on mobile'))
              : WebViewWidget(controller: _controller),
    );
  }
}
