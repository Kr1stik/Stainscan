import 'package:flutter/material.dart';
import 'package:flutter/widgets.dart';

Widget buildImageRendererImpl(String imagePath) {
  return Image.network(
    imagePath,
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
