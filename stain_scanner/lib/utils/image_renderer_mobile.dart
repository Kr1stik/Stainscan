import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter/widgets.dart';

Widget buildImageRendererImpl(String imagePath) {
  final file = File(imagePath);
  if (file.existsSync()) {
    return Image.file(
      file,
      fit: BoxFit.cover,
      errorBuilder: (context, error, stackTrace) {
        return Center(
          child: Icon(
            Icons.image_not_supported,
            size: 64,
            color: Colors.grey.shade400,
          ),
        );
      },
    );
  }

  return Center(
    child: Icon(
      Icons.image_not_supported,
      size: 64,
      color: Colors.grey.shade400,
    ),
  );
}
