import 'package:flutter/widgets.dart';
import 'image_renderer_mobile.dart'
    if (dart.library.html) 'image_renderer_web.dart';

Widget buildImageRenderer(String imagePath) => buildImageRendererImpl(imagePath);
