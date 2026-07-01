from playwright.sync_api import sync_playwright

def verify():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto('file:///app/social-stratification-simulator.html')
        page.wait_for_timeout(2000)
        page.screenshot(path='v11_3d_check.png')

        # Check if 3D Canvas exists
        canvas = page.query_selector('#simulationCanvas')
        if canvas:
            print("3D Canvas found.")

        # Check if 3D Camera Controls Legend exists
        legend = page.query_selector('.camera-legend')
        if legend:
            print("Camera legend found.")

        browser.close()

if __name__ == "__main__":
    verify()
