import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';

/// Phone-first authentication layout shared by Login and Sign Up.
///
/// A slate hero header with a curved bottom edge sits above a parchment sheet
/// that overlaps it by 32px. The sheet scrolls when the keyboard is open and
/// respects the bottom safe-area inset.
class AuthPageShell extends StatelessWidget {
  const AuthPageShell({super.key, required this.header, required this.child});

  final Widget header;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    final double bottomInset = MediaQuery.paddingOf(context).bottom;

    return Scaffold(
      backgroundColor: AppColors.canvas,
      resizeToAvoidBottomInset: true,
      body: LayoutBuilder(
        builder: (BuildContext context, BoxConstraints constraints) {
          return SingleChildScrollView(
            keyboardDismissBehavior: ScrollViewKeyboardDismissBehavior.onDrag,
            child: ConstrainedBox(
              constraints: BoxConstraints(minHeight: constraints.maxHeight),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: <Widget>[
                  header,
                  Transform.translate(
                    offset: const Offset(0, -32),
                    child: Container(
                      decoration: const BoxDecoration(
                        color: AppColors.authSheet,
                        borderRadius: BorderRadius.vertical(
                          top: Radius.circular(32),
                        ),
                        boxShadow: <BoxShadow>[
                          BoxShadow(
                            color: AppColors.authSheetShadow,
                            offset: Offset(0, -12),
                            blurRadius: 28,
                            spreadRadius: -16,
                          ),
                        ],
                      ),
                      padding: EdgeInsets.fromLTRB(
                        24,
                        40,
                        24,
                        24 + bottomInset,
                      ),
                      child: child,
                    ),
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}
