import 'dart:convert';
import 'dart:io';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:http/http.dart' as http;

import '../../core/constants/api_endpoints.dart';

/// Standard exception thrown by [ApiService] upon failed HTTP operations.
class ApiException implements Exception {
  const ApiException({
    required this.statusCode,
    required this.message,
    this.details,
  });

  final int statusCode;
  final String message;
  final dynamic details;

  @override
  String toString() => 'ApiException($statusCode): $message';
}

/// Core HTTP client service for MedOracle backend connectivity.
class ApiService {
  ApiService({
    http.Client? client,
    String? baseUrl,
  })  : _client = client ?? http.Client(),
        _baseUrl = baseUrl ?? ApiEndpoints.baseUrl;

  final http.Client _client;
  final String _baseUrl;
  String? _authToken;

  /// Duration before requests time out.
  static const Duration defaultTimeout = Duration(seconds: 10);

  /// Sets or clears the Bearer JWT token for subsequent requests.
  void setAuthToken(String? token) {
    _authToken = token;
  }

  String? get authToken => _authToken;

  Map<String, String> _buildHeaders(Map<String, String>? extraHeaders) {
    final Map<String, String> headers = <String, String>{
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };
    if (_authToken != null && _authToken!.isNotEmpty) {
      headers['Authorization'] = 'Bearer $_authToken';
    }
    if (extraHeaders != null) {
      headers.addAll(extraHeaders);
    }
    return headers;
  }

  Uri _buildUri(String endpoint, [Map<String, dynamic>? queryParameters]) {
    final String cleanBase = _baseUrl.endsWith('/')
        ? _baseUrl.substring(0, _baseUrl.length - 1)
        : _baseUrl;
    final String cleanEndpoint =
        endpoint.startsWith('/') ? endpoint : '/$endpoint';
    final Uri baseUri = Uri.parse('$cleanBase$cleanEndpoint');

    if (queryParameters != null && queryParameters.isNotEmpty) {
      final Map<String, String> stringParams = queryParameters.map(
        (key, value) => MapEntry(key, value.toString()),
      );
      return baseUri.replace(queryParameters: stringParams);
    }
    return baseUri;
  }

  Future<dynamic> get(
    String endpoint, {
    Map<String, String>? headers,
    Map<String, dynamic>? queryParameters,
  }) async {
    final Uri uri = _buildUri(endpoint, queryParameters);
    try {
      final http.Response response = await _client
          .get(uri, headers: _buildHeaders(headers))
          .timeout(defaultTimeout);
      return _processResponse(response);
    } on SocketException catch (e) {
      throw ApiException(statusCode: 0, message: 'Network connection error: ${e.message}');
    } on http.ClientException catch (e) {
      throw ApiException(statusCode: 0, message: 'HTTP client error: ${e.message}');
    }
  }

  Future<dynamic> post(
    String endpoint, {
    Map<String, String>? headers,
    Object? body,
  }) async {
    final Uri uri = _buildUri(endpoint);
    try {
      final http.Response response = await _client
          .post(
            uri,
            headers: _buildHeaders(headers),
            body: body != null ? jsonEncode(body) : null,
          )
          .timeout(defaultTimeout);
      return _processResponse(response);
    } on SocketException catch (e) {
      throw ApiException(statusCode: 0, message: 'Network connection error: ${e.message}');
    } on http.ClientException catch (e) {
      throw ApiException(statusCode: 0, message: 'HTTP client error: ${e.message}');
    }
  }

  Future<dynamic> put(
    String endpoint, {
    Map<String, String>? headers,
    Object? body,
  }) async {
    final Uri uri = _buildUri(endpoint);
    try {
      final http.Response response = await _client
          .put(
            uri,
            headers: _buildHeaders(headers),
            body: body != null ? jsonEncode(body) : null,
          )
          .timeout(defaultTimeout);
      return _processResponse(response);
    } on SocketException catch (e) {
      throw ApiException(statusCode: 0, message: 'Network connection error: ${e.message}');
    } on http.ClientException catch (e) {
      throw ApiException(statusCode: 0, message: 'HTTP client error: ${e.message}');
    }
  }

  Future<dynamic> delete(
    String endpoint, {
    Map<String, String>? headers,
  }) async {
    final Uri uri = _buildUri(endpoint);
    try {
      final http.Response response = await _client
          .delete(uri, headers: _buildHeaders(headers))
          .timeout(defaultTimeout);
      return _processResponse(response);
    } on SocketException catch (e) {
      throw ApiException(statusCode: 0, message: 'Network connection error: ${e.message}');
    } on http.ClientException catch (e) {
      throw ApiException(statusCode: 0, message: 'HTTP client error: ${e.message}');
    }
  }

  dynamic _processResponse(http.Response response) {
    dynamic decoded;
    if (response.body.isNotEmpty) {
      try {
        decoded = jsonDecode(response.body);
      } catch (_) {
        decoded = response.body;
      }
    }

    if (response.statusCode >= 200 && response.statusCode < 300) {
      return decoded;
    }

    String message = 'Request failed with status code ${response.statusCode}';
    if (decoded is Map && decoded.containsKey('detail')) {
      final dynamic detail = decoded['detail'];
      message = detail is String ? detail : jsonEncode(detail);
    }

    throw ApiException(
      statusCode: response.statusCode,
      message: message,
      details: decoded,
    );
  }
}

/// Global provider for [ApiService].
final Provider<ApiService> apiServiceProvider = Provider<ApiService>((Ref ref) {
  return ApiService();
});
