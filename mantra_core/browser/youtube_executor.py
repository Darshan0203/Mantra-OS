import asyncio
import subprocess
from playwright.async_api import async_playwright


class YouTubeExecutor:

    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    # ================================================================
    # ADB
    # ================================================================

    def _adb(self, *args):
        command = ["adb", *args]

        print("[ADB]", " ".join(command))

        result = subprocess.run(
            command,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"ADB command failed:\n{result.stderr.strip()}"
            )

        return result.stdout.strip()

    # ================================================================
    # LAUNCH CHROME
    # ================================================================

    def _launch_chrome(self):
        print("[YOUTUBE] Launching Chrome on Android...")

        self._adb(
            "shell",
            "am",
            "force-stop",
            "com.android.chrome"
        )

        self._adb(
            "shell",
            "am",
            "start",
            "-n",
            "com.android.chrome/"
            "com.google.android.apps.chrome.Main"
        )

        self._adb(
            "forward",
            "tcp:9222",
            "localabstract:chrome_devtools_remote"
        )

        print("[YOUTUBE] Android Chrome launched.")

    # ================================================================
    # START
    # ================================================================

    async def start(self):
        print("[YOUTUBE] Starting Android YouTube session...")

        self._launch_chrome()

        print("[YOUTUBE] Waiting for Chrome DevTools...")

        for attempt in range(20):

            try:
                result = subprocess.run(
                    [
                        "curl",
                        "-s",
                        "http://127.0.0.1:9222/json/version"
                    ],
                    capture_output=True,
                    text=True,
                    timeout=3
                )

                if (
                    result.returncode == 0
                    and "webSocketDebuggerUrl" in result.stdout
                ):
                    print(
                        "[YOUTUBE] Chrome DevTools is ready."
                    )
                    break

            except Exception:
                pass

            print(
                f"[YOUTUBE] Waiting for Chrome... "
                f"{attempt + 1}/20"
            )

            await asyncio.sleep(1)

        else:
            raise RuntimeError(
                "Chrome DevTools did not become available."
            )

        self.playwright = await async_playwright().start()

        print(
            "[YOUTUBE] Connecting Playwright "
            "to Android Chrome..."
        )

        self.browser = (
            await self.playwright.chromium.connect_over_cdp(
                "http://127.0.0.1:9222"
            )
        )

        contexts = self.browser.contexts

        if not contexts:
            raise RuntimeError(
                "No Chrome browser context found."
            )

        self.context = contexts[0]

        pages = self.context.pages

        if not pages:
            raise RuntimeError(
                "Chrome launched but no tab was found."
            )

        self.page = pages[0]

        print(
            "[YOUTUBE] Connected to Android Chrome."
        )

        print(
            f"[YOUTUBE] Current page: {self.page.url}"
        )

    # ================================================================
    # OPEN YOUTUBE
    # ================================================================

    async def open_youtube(self):
        if not self.page:
            raise RuntimeError(
                "YouTube browser page is not available."
            )

        print(
            "[YOUTUBE] Opening YouTube in desktop mode..."
        )

        await self.page.set_extra_http_headers({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/153.0.0.0 Safari/537.36"
            )
        })

        await self.page.goto(
            "https://www.youtube.com",
            wait_until="domcontentloaded"
        )

        await self.page.wait_for_timeout(5000)

        print(
            "[YOUTUBE] YouTube opened."
        )

    # ================================================================
    # SEARCH
    # ================================================================

    async def search(self, query):
        if not self.page:
            raise RuntimeError(
                "YouTube browser page is not available."
            )

        print(
            f"[YOUTUBE] Searching: {query}"
        )

        search_box = self.page.locator(
            'input[name="search_query"]'
        )

        await search_box.wait_for(
            state="visible",
            timeout=15000
        )

        await search_box.fill(query)

        await search_box.press("Enter")

        await self.page.wait_for_timeout(4000)

        print(
            "[YOUTUBE] Search completed."
        )

    # ================================================================
    # OPEN FIRST RESULT
    # ================================================================

    async def open_first_result(self):
        if not self.page:
            raise RuntimeError(
                "YouTube browser page is not available."
            )

        print(
            "[YOUTUBE] Opening first video..."
        )

        video = self.page.locator(
            "ytd-video-renderer a#video-title"
        ).first

        await video.wait_for(
            state="visible",
            timeout=15000
        )

        title = await video.get_attribute(
            "title"
        )

        print(
            f"[YOUTUBE] First video: {title}"
        )

        await video.click()

        await self.page.wait_for_timeout(5000)

        print(
            "[YOUTUBE] First video opened."
        )

    # ================================================================
    # GET URL
    # ================================================================

    async def get_current_url(self):
        if not self.page:
            raise RuntimeError(
                "YouTube browser page is not available."
            )

        url = self.page.url

        print(
            f"[YOUTUBE] Video URL: {url}"
        )

        return url

    # ================================================================
    # RETURN TO MANTRA
    # ================================================================

    def _return_to_mantra(self):
        print(
            "[YOUTUBE] Returning to MANTRA..."
        )

        self._adb(
            "shell",
            "am",
            "force-stop",
            "com.android.chrome"
        )

        self._adb(
            "shell",
            "monkey",
            "-p",
            "com.mantraos",
            "1"
        )

        print(
            "[YOUTUBE] MANTRA is now foreground."
        )

    # ================================================================
    # CLOSE
    # ================================================================

    async def close(self):
        print(
            "[YOUTUBE] Closing YouTube session..."
        )

        try:

            if self.page:
                try:
                    await self.page.close()
                except Exception:
                    pass

            self.page = None
            self.context = None
            self.browser = None

            if self.playwright:
                try:
                    await self.playwright.stop()
                except Exception:
                    pass

            self.playwright = None

        finally:

            try:
                self._return_to_mantra()
            except Exception as e:
                print(
                    f"[YOUTUBE] Could not return "
                    f"to MANTRA: {e}"
                )

        print(
            "[YOUTUBE] YouTube session finished."
        )


# ================================================================
# STANDALONE TEST
# ================================================================

async def main():

    youtube = YouTubeExecutor()

    try:

        await youtube.start()

        await youtube.open_youtube()

        await youtube.search(
            "Python tutorials"
        )

        await youtube.open_first_result()

        url = await youtube.get_current_url()

        print("\n================================")
        print("YOUTUBE TEST SUCCESS")
        print("VIDEO URL:")
        print(url)
        print("================================")

        await asyncio.sleep(3)

    except Exception as e:

        print("\n================================")
        print("YOUTUBE TEST FAILED")
        print(str(e))
        print("================================")

    finally:

        await youtube.close()


if __name__ == "__main__":
    asyncio.run(main())