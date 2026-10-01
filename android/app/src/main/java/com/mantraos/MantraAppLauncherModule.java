package com.mantraos;

import android.content.Intent;
import android.content.pm.PackageManager;
import android.util.Log;

import androidx.annotation.NonNull;

import com.facebook.react.bridge.ReactApplicationContext;
import com.facebook.react.bridge.ReactContextBaseJavaModule;
import com.facebook.react.bridge.ReactMethod;

public class MantraAppLauncherModule extends ReactContextBaseJavaModule {

    private static final String TAG = "MANTRA_LAUNCHER";

    private final ReactApplicationContext reactContext;

    public MantraAppLauncherModule(ReactApplicationContext reactContext) {
        super(reactContext);
        this.reactContext = reactContext;
    }

    @NonNull
    @Override
    public String getName() {
        return "MantraAppLauncher";
    }

    // ==========================================
    // Launch Android App
    // ==========================================

    @ReactMethod
    public void launchApp(String packageName) {

        Log.d(TAG, "================================");
        Log.d(TAG, "MANTRA LAUNCH REQUEST");
        Log.d(TAG, "Package: " + packageName);

        try {

            PackageManager packageManager =
                    reactContext.getPackageManager();

            Intent intent =
                    packageManager.getLaunchIntentForPackage(packageName);

            if (intent == null) {
                Log.e(TAG,
                        "NO LAUNCH INTENT FOUND FOR: "
                                + packageName);
                return;
            }

            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);

            Log.d(TAG, "Starting Android activity...");

            reactContext.startActivity(intent);

            Log.d(TAG,
                    "Activity launch requested successfully.");

        } catch (Exception e) {

            Log.e(TAG,
                    "FAILED TO LAUNCH APP",
                    e);
        }

        Log.d(TAG, "================================");
    }

    // ==========================================
    // YouTube Search through Accessibility
    // ==========================================

    @ReactMethod
    public void searchYouTube(String query) {

        Log.d(TAG, "================================");
        Log.d(TAG, "MANTRA YOUTUBE SEARCH REQUEST");
        Log.d(TAG, "Query: " + query);

        boolean success =
                MantraAccessibilityService.searchYouTube(query);

        if (success) {
            Log.d(TAG,
                    "YouTube search request successful.");
        } else {
            Log.e(TAG,
                    "YouTube search request failed.");
        }

        Log.d(TAG, "================================");
    }
@ReactMethod
public void openWhatsAppContact(String contact) {
    Log.d(TAG, "Opening WhatsApp contact: " + contact);
    MantraAccessibilityService.openWhatsAppContact(contact);
}

@ReactMethod
public void sendWhatsAppMessage(String message) {
    Log.d(TAG, "Sending WhatsApp message: " + message);
    MantraAccessibilityService.sendWhatsAppMessage(message);
}

@ReactMethod
public void returnToMantra() {
    try {
        PackageManager packageManager =
                reactContext.getPackageManager();

        Intent intent =
                packageManager.getLaunchIntentForPackage(
                        reactContext.getPackageName()
                );

        if (intent != null) {
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            reactContext.startActivity(intent);
        }
    } catch (Exception e) {
        Log.e(TAG, "Failed to return to MANTRA", e);
    }
}

}