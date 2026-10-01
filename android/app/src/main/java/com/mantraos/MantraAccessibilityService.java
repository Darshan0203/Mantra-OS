package com.mantraos;

import android.accessibilityservice.AccessibilityService;
import android.accessibilityservice.GestureDescription;
import android.graphics.Path;
import android.graphics.Rect;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.util.DisplayMetrics;
import android.util.Log;
import android.view.accessibility.AccessibilityEvent;
import android.view.accessibility.AccessibilityNodeInfo;

import java.util.List;

public class MantraAccessibilityService extends AccessibilityService {
    private static final String TAG = "MANTRA_ACCESSIBILITY";
    private static final String YOUTUBE = "com.google.android.youtube";
    private static MantraAccessibilityService instance;
    private final Handler handler = new Handler(Looper.getMainLooper());

    @Override
    protected void onServiceConnected() {
        super.onServiceConnected();
        instance = this;
        Log.d(TAG, "MANTRA Accessibility Service connected");
    }

    @Override
    public void onAccessibilityEvent(AccessibilityEvent event) {
        if (event == null) return;
        CharSequence packageName = event.getPackageName();
        if (packageName != null) {
            Log.d(TAG, "Accessibility event from: " + packageName);
        }
    }

    @Override
    public void onInterrupt() {
        Log.d(TAG, "MANTRA Accessibility Service interrupted.");
    }

    // YOUTUBE
    public static boolean searchYouTube(String query) {
        if (instance == null) {
            Log.e(TAG, "Accessibility service is not connected.");
            return false;
        }
        Log.d(TAG, "================================");
        Log.d(TAG, "MANTRA YOUTUBE SEARCH");
        Log.d(TAG, "Query: " + query);
        Log.d(TAG, "================================");
        instance.openYouTubeSearch(query);
        return true;
    }

    private void openYouTubeSearch(String query) {
        findSearchButton(query, 0);
    }

    private void findSearchButton(String query, int attempt) {
        final int MAX_ATTEMPTS = 20;
        if (attempt >= MAX_ATTEMPTS) {
            Log.d(TAG, "Accessibility Search button not found.");
            Log.d(TAG, "Using top-right coordinate fallback.");
            tapYouTubeSearchIcon(query);
            return;
        }

        handler.postDelayed(() -> {
            AccessibilityNodeInfo root = getRootInActiveWindow();

            if (root == null) {
                Log.d(TAG, "YouTube root unavailable. Retrying...");
                findSearchButton(query, attempt + 1);
                return;
            }

            CharSequence packageName = root.getPackageName();

            if (packageName == null || !YOUTUBE.contentEquals(packageName)) {
                Log.d(TAG, "Current window is not YouTube: " + packageName);
                findSearchButton(query, attempt + 1);
                return;
            }

            AccessibilityNodeInfo searchButton = findSearchButtonNode(root);

            if (searchButton != null) {
                Log.d(TAG, "YouTube Search button FOUND.");
                clickSearchButton(searchButton, query);
                return;
            }

            Log.d(TAG, "Search button not found. Attempt: " + (attempt + 1));
            findSearchButton(query, attempt + 1);
        }, 400);
    }

    private AccessibilityNodeInfo findSearchButtonNode(AccessibilityNodeInfo root) {
        if (root == null) return null;

        String[] texts = {"Search", "Search YouTube"};

        for (String text : texts) {
            try {
                List<AccessibilityNodeInfo> nodes = root.findAccessibilityNodeInfosByText(text);
                if (nodes == null) continue;

                for (AccessibilityNodeInfo node : nodes) {
                    if (node == null || !node.isVisibleToUser()) continue;

                    CharSequence nodeText = node.getText();
                    CharSequence description = node.getContentDescription();

                    if (node.isClickable() &&
                            ((nodeText != null && text.contentEquals(nodeText)) ||
                             (description != null && text.contentEquals(description)))) {
                        Rect bounds = new Rect();
                        node.getBoundsInScreen(bounds);
                        Log.d(TAG, "Search node bounds: " + bounds);
                        return node;
                    }
                }
            } catch (Exception e) {
                Log.e(TAG, "Search node lookup error", e);
            }
        }

        return findSearchButtonRecursive(root);
    }

    private AccessibilityNodeInfo findSearchButtonRecursive(AccessibilityNodeInfo node) {
        if (node == null) return null;

        if (node.isVisibleToUser() && node.isClickable()) {
            CharSequence description = node.getContentDescription();
            CharSequence text = node.getText();

            if ((description != null && description.toString().toLowerCase().contains("search")) ||
                (text != null && text.toString().toLowerCase().contains("search"))) {
                Rect bounds = new Rect();
                node.getBoundsInScreen(bounds);

                if (bounds.top < getScreenHeight() * 0.25) {
                    Log.d(TAG, "Recursive Search button found: " + bounds);
                    return node;
                }
            }
        }

        for (int i = 0; i < node.getChildCount(); i++) {
            AccessibilityNodeInfo result = findSearchButtonRecursive(node.getChild(i));
            if (result != null) return result;
        }

        return null;
    }

    private void clickSearchButton(AccessibilityNodeInfo node, String query) {
        Rect bounds = new Rect();
        node.getBoundsInScreen(bounds);
        Log.d(TAG, "Clicking YouTube Search: " + bounds);

        boolean clicked = node.performAction(AccessibilityNodeInfo.ACTION_CLICK);
        Log.d(TAG, "Accessibility Search click: " + clicked);

        if (!clicked) {
            clickAt(bounds.centerX(), bounds.centerY());
        }

        waitForSearchInput(query, 0);
    }

    private void tapYouTubeSearchIcon(String query) {
        DisplayMetrics metrics = getResources().getDisplayMetrics();
        float density = metrics.density;
        float x = metrics.widthPixels - (40 * density);
        float y = 34 * density;

        Log.d(TAG, "================================");
        Log.d(TAG, "YOUTUBE SEARCH COORDINATE FALLBACK");
        Log.d(TAG, "Screen width: " + metrics.widthPixels);
        Log.d(TAG, "Density: " + density);
        Log.d(TAG, "Tap X: " + x);
        Log.d(TAG, "Tap Y: " + y);
        Log.d(TAG, "================================");

        clickAt(x, y);

        handler.postDelayed(() -> waitForSearchInput(query, 0), 1000);
    }

    private void waitForSearchInput(String query, int attempt) {
        final int MAX_ATTEMPTS = 20;

        if (attempt >= MAX_ATTEMPTS) {
            Log.e(TAG, "YouTube search input not found.");
            return;
        }

        handler.postDelayed(() -> {
            AccessibilityNodeInfo root = getRootInActiveWindow();

            if (root == null) {
                Log.d(TAG, "Root unavailable. Retrying input...");
                waitForSearchInput(query, attempt + 1);
                return;
            }

            CharSequence packageName = root.getPackageName();

            if (packageName == null || !YOUTUBE.contentEquals(packageName)) {
                Log.d(TAG, "Waiting for YouTube search screen: " + packageName);
                waitForSearchInput(query, attempt + 1);
                return;
            }

            AccessibilityNodeInfo input = findEditableNode(root);

            if (input == null) {
                Log.d(TAG, "Search input not available. Attempt: " + (attempt + 1));
                waitForSearchInput(query, attempt + 1);
                return;
            }

            Log.d(TAG, "YouTube search input FOUND.");
            enterSearchText(input, query);
        }, 400);
    }

    private AccessibilityNodeInfo findEditableNode(AccessibilityNodeInfo node) {
        if (node == null) return null;

        if (node.isVisibleToUser() && node.isEditable()) {
            return node;
        }

        for (int i = 0; i < node.getChildCount(); i++) {
            AccessibilityNodeInfo result = findEditableNode(node.getChild(i));
            if (result != null) return result;
        }

        return null;
    }

    private void enterSearchText(AccessibilityNodeInfo input, String query) {
        Log.d(TAG, "Clicking YouTube input.");

        boolean clicked = input.performAction(AccessibilityNodeInfo.ACTION_CLICK);
        Log.d(TAG, "Input click result: " + clicked);

        handler.postDelayed(() -> {
            Bundle arguments = new Bundle();
            arguments.putCharSequence(
                    AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE,
                    query
            );

            boolean entered = input.performAction(
                    AccessibilityNodeInfo.ACTION_SET_TEXT,
                    arguments
            );

            Log.d(TAG, "Search text entered: " + entered);
            handler.postDelayed(() -> verifySearchText(query), 500);
        }, 300);
    }

    private void verifySearchText(String query) {
        AccessibilityNodeInfo root = getRootInActiveWindow();

        if (root == null) {
            Log.e(TAG, "Cannot verify search text.");
            return;
        }

        CharSequence packageName = root.getPackageName();

        if (packageName == null || !YOUTUBE.contentEquals(packageName)) {
            Log.e(TAG, "Verification failed. Current app: " + packageName);
            return;
        }

        AccessibilityNodeInfo input = findEditableNode(root);

        if (input == null) {
            Log.e(TAG, "Search input disappeared.");
            return;
        }

        CharSequence currentText = input.getText();
        Log.d(TAG, "YouTube input text: " + currentText);

        if (currentText != null && query.contentEquals(currentText)) {
            Log.d(TAG, "================================");
            Log.d(TAG, "SEARCH VERIFIED");
            Log.d(TAG, "Query: " + query);
            Log.d(TAG, "================================");
        } else {
            Log.e(TAG, "SEARCH TEXT VERIFICATION FAILED");
        }
    }

    // WHATSAPP
    public static boolean openWhatsAppContact(String contact) {
        if (instance == null) {
            Log.e(TAG, "Accessibility service is not connected.");
            return false;
        }

        Log.d(TAG, "Opening WhatsApp contact: " + contact);
        instance.findWhatsAppSearch(contact, 0);
        return true;
    }

    public static boolean sendWhatsAppMessage(String message) {
        if (instance == null) {
            Log.e(TAG, "Accessibility service is not connected.");
            return false;
        }

        Log.d(TAG, "Sending WhatsApp message: " + message);
        instance.findWhatsAppInput(message, 0);
        return true;
    }

    private void findWhatsAppSearch(String contact, int attempt) {
    final int MAX_ATTEMPTS = 10;

    if (attempt >= MAX_ATTEMPTS) {
        Log.e(TAG, "WhatsApp search button not found.");
        Log.d(TAG, "Using WhatsApp search coordinate fallback.");
        tapWhatsAppSearchIcon(contact);
        return;
    }

    handler.postDelayed(() -> {
        AccessibilityNodeInfo root = getRootInActiveWindow();

        if (root == null) {
            findWhatsAppSearch(contact, attempt + 1);
            return;
        }

        Log.d(TAG, "WhatsApp root package: " + root.getPackageName());

        AccessibilityNodeInfo search = findWhatsAppSearchNode(root);

        if (search != null) {
            Rect bounds = new Rect();
            search.getBoundsInScreen(bounds);

            Log.d(TAG, "WhatsApp search node FOUND: " + bounds);

            boolean clicked = search.performAction(
                    AccessibilityNodeInfo.ACTION_CLICK
            );

            Log.d(TAG, "WhatsApp search clicked: " + clicked);

            if (!clicked) {
                clickAt(bounds.centerX(), bounds.centerY());
            }

            handler.postDelayed(
                    () -> findWhatsAppSearchInput(contact, 0),
                    700
            );
            return;
        }

        Log.d(TAG, "WhatsApp search node not found. Attempt: " + (attempt + 1));
        findWhatsAppSearch(contact, attempt + 1);

    }, 500);
}

private void tapWhatsAppSearchIcon(String contact) {
    DisplayMetrics metrics = getResources().getDisplayMetrics();

    float x = metrics.widthPixels - (55 * metrics.density);
    float y = 45 * metrics.density;

    Log.d(TAG, "================================");
    Log.d(TAG, "WHATSAPP SEARCH COORDINATE FALLBACK");
    Log.d(TAG, "Screen width: " + metrics.widthPixels);
    Log.d(TAG, "Density: " + metrics.density);
    Log.d(TAG, "Tap X: " + x);
    Log.d(TAG, "Tap Y: " + y);
    Log.d(TAG, "================================");

    clickAt(x, y);

    handler.postDelayed(
            () -> findWhatsAppSearchInput(contact, 0),
            1000
    );
}

    private AccessibilityNodeInfo findWhatsAppSearchNode(AccessibilityNodeInfo node) {
        if (node == null) return null;

        if (node.isVisibleToUser()) {
            CharSequence text = node.getText();
            CharSequence description = node.getContentDescription();

            String textValue = text == null ? "" : text.toString().toLowerCase();
            String descriptionValue = description == null ? "" : description.toString().toLowerCase();

            boolean looksLikeSearch =
                    textValue.contains("search") ||
                    descriptionValue.contains("search");

            if (looksLikeSearch) {
                Rect bounds = new Rect();
                node.getBoundsInScreen(bounds);

                Log.d(TAG,
                        "Possible WhatsApp search node: text=" + text +
                        ", description=" + description +
                        ", clickable=" + node.isClickable() +
                        ", bounds=" + bounds);

                if (node.isClickable()) {
                    return node;
                }

                AccessibilityNodeInfo parent = node.getParent();

                while (parent != null) {
                    if (parent.isVisibleToUser() && parent.isClickable()) {
                        Rect parentBounds = new Rect();
                        parent.getBoundsInScreen(parentBounds);
                        Log.d(TAG, "Clickable search parent found: " + parentBounds);
                        return parent;
                    }

                    parent = parent.getParent();
                }
            }
        }

        for (int i = 0; i < node.getChildCount(); i++) {
            AccessibilityNodeInfo result = findWhatsAppSearchNode(node.getChild(i));
            if (result != null) return result;
        }

        return null;
    }

    private void findWhatsAppSearchInput(String contact, int attempt) {
        final int MAX_ATTEMPTS = 20;

        if (attempt >= MAX_ATTEMPTS) {
            Log.e(TAG, "WhatsApp search input not found.");
            return;
        }

        handler.postDelayed(() -> {
            AccessibilityNodeInfo root = getRootInActiveWindow();

            if (root == null) {
                findWhatsAppSearchInput(contact, attempt + 1);
                return;
            }

            AccessibilityNodeInfo input = findEditableNode(root);

            if (input != null) {
                Bundle arguments = new Bundle();
                arguments.putCharSequence(
                        AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE,
                        contact
                );

                boolean entered = input.performAction(
                        AccessibilityNodeInfo.ACTION_SET_TEXT,
                        arguments
                );

                Log.d(TAG, "WhatsApp contact search entered: " + entered);
                findWhatsAppContactResult(contact, 0);
                return;
            }

            findWhatsAppSearchInput(contact, attempt + 1);
        }, 500);
    }

    private void findWhatsAppContactResult(String contact, int attempt) {
        final int MAX_ATTEMPTS = 20;

        if (attempt >= MAX_ATTEMPTS) {
            Log.e(TAG, "WhatsApp contact result not found.");
            return;
        }

        handler.postDelayed(() -> {
            AccessibilityNodeInfo root = getRootInActiveWindow();

            if (root == null) {
                findWhatsAppContactResult(contact, attempt + 1);
                return;
            }

            AccessibilityNodeInfo contactNode = findNodeByText(root, contact);

            if (contactNode != null) {
                Log.d(TAG, "WhatsApp contact found: " + contact);

                AccessibilityNodeInfo clickable = contactNode;

                while (clickable != null && !clickable.isClickable()) {
                    clickable = clickable.getParent();
                }

                if (clickable != null) {
                    boolean clicked = clickable.performAction(
                            AccessibilityNodeInfo.ACTION_CLICK
                    );

                    Log.d(TAG, "WhatsApp contact clicked: " + clicked);
                    Log.d(TAG, "WhatsApp contact opened.");
                }

                return;
            }

            findWhatsAppContactResult(contact, attempt + 1);
        }, 500);
    }

    private void findWhatsAppInput(String message, int attempt) {
        final int MAX_ATTEMPTS = 20;

        if (attempt >= MAX_ATTEMPTS) {
            Log.e(TAG, "WhatsApp message input not found.");
            return;
        }

        handler.postDelayed(() -> {
            AccessibilityNodeInfo root = getRootInActiveWindow();

            if (root == null) {
                findWhatsAppInput(message, attempt + 1);
                return;
            }

            AccessibilityNodeInfo input = findEditableNode(root);

            if (input != null) {
                Bundle arguments = new Bundle();
                arguments.putCharSequence(
                        AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE,
                        message
                );

                boolean entered = input.performAction(
                        AccessibilityNodeInfo.ACTION_SET_TEXT,
                        arguments
                );

                Log.d(TAG, "WhatsApp message entered: " + entered);

                handler.postDelayed(
                        () -> clickWhatsAppSendButton(0),
                        700
                );

                return;
            }

            findWhatsAppInput(message, attempt + 1);
        }, 500);
    }

    private void clickWhatsAppSendButton(int attempt) {
        final int MAX_ATTEMPTS = 20;

        if (attempt >= MAX_ATTEMPTS) {
            Log.e(TAG, "WhatsApp Send button not found.");
            return;
        }

        handler.postDelayed(() -> {
            AccessibilityNodeInfo root = getRootInActiveWindow();

            if (root == null) {
                clickWhatsAppSendButton(attempt + 1);
                return;
            }

            AccessibilityNodeInfo send = findWhatsAppSendNode(root);

            if (send != null) {
                Rect bounds = new Rect();
                send.getBoundsInScreen(bounds);

                Log.d(TAG, "WhatsApp Send node FOUND: " + bounds);

                boolean clicked = send.performAction(
                        AccessibilityNodeInfo.ACTION_CLICK
                );

                Log.d(TAG, "WhatsApp Send clicked: " + clicked);

                if (!clicked) {
                    clickAt(bounds.centerX(), bounds.centerY());
                }

                return;
            }

            clickWhatsAppSendButton(attempt + 1);
        }, 500);
    }

    private AccessibilityNodeInfo findWhatsAppSendNode(AccessibilityNodeInfo node) {
        if (node == null) return null;

        if (node.isVisibleToUser()) {
            CharSequence text = node.getText();
            CharSequence description = node.getContentDescription();

            String textValue = text == null ? "" : text.toString().toLowerCase();
            String descriptionValue = description == null ? "" : description.toString().toLowerCase();

            boolean looksLikeSend =
                    textValue.contains("send") ||
                    descriptionValue.contains("send");

            if (looksLikeSend) {
                Rect bounds = new Rect();
                node.getBoundsInScreen(bounds);

                Log.d(TAG,
                        "Possible WhatsApp Send node: text=" + text +
                        ", description=" + description +
                        ", clickable=" + node.isClickable() +
                        ", bounds=" + bounds);

                if (node.isClickable()) {
                    return node;
                }

                AccessibilityNodeInfo parent = node.getParent();

                while (parent != null) {
                    if (parent.isVisibleToUser() && parent.isClickable()) {
                        return parent;
                    }

                    parent = parent.getParent();
                }
            }
        }

        for (int i = 0; i < node.getChildCount(); i++) {
            AccessibilityNodeInfo result = findWhatsAppSendNode(node.getChild(i));
            if (result != null) return result;
        }

        return null;
    }

    // HELPERS
    private AccessibilityNodeInfo findNodeByText(
            AccessibilityNodeInfo node,
            String text
    ) {
        if (node == null) return null;

        CharSequence nodeText = node.getText();

        if (node.isVisibleToUser() &&
                nodeText != null &&
                text.equalsIgnoreCase(nodeText.toString().trim())) {
            return node;
        }

        for (int i = 0; i < node.getChildCount(); i++) {
            AccessibilityNodeInfo result =
                    findNodeByText(node.getChild(i), text);

            if (result != null) return result;
        }

        return null;
    }

    private AccessibilityNodeInfo findNodeByContentDescription(
            AccessibilityNodeInfo node,
            String description
    ) {
        if (node == null) return null;

        CharSequence contentDescription =
                node.getContentDescription();

        if (node.isVisibleToUser() &&
                contentDescription != null &&
                contentDescription.toString()
                        .toLowerCase()
                        .contains(description.toLowerCase())) {
            return node;
        }

        for (int i = 0; i < node.getChildCount(); i++) {
            AccessibilityNodeInfo result =
                    findNodeByContentDescription(
                            node.getChild(i),
                            description
                    );

            if (result != null) return result;
        }

        return null;
    }

    private int getScreenHeight() {
        return getResources()
                .getDisplayMetrics()
                .heightPixels;
    }

    private boolean clickAt(float x, float y) {
        if (android.os.Build.VERSION.SDK_INT <
                android.os.Build.VERSION_CODES.N) {
            Log.e(TAG, "Gesture API requires Android 7.0+.");
            return false;
        }

        Path path = new Path();
        path.moveTo(x, y);

        GestureDescription gesture =
                new GestureDescription.Builder()
                        .addStroke(
                                new GestureDescription.StrokeDescription(
                                        path,
                                        0,
                                        100
                                )
                        )
                        .build();

        boolean dispatched =
                dispatchGesture(
                        gesture,
                        null,
                        null
                );

        Log.d(TAG, "Gesture dispatched: " + dispatched);

        return dispatched;
    }
}