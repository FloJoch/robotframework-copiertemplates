*** Settings ***
Documentation       Hello world for mobile: opens an entry of the Android settings. Runs only with the
...                 profile "mobile" (Appium server and Android device or emulator): uv run robotcode -p mobile robot
Resource            ${EXECDIR}/resources/tasks/mobile_tasks.resource
Resource            ${EXECDIR}/resources/assertions/mobile_assertions.resource
Test Setup          Start Settings App
Test Teardown       Stop App
Test Tags           mobile    hello-world    requires-device


*** Test Cases ***
Display Settings Can Be Opened
    [Documentation]    The entry "Display" opens the display settings.
    Open Setting    Display
    Screen Should Show Text    Display
