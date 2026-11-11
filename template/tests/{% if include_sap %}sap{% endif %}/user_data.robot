*** Settings ***
Documentation       Hello world for SAP: opens your own user data. Runs only with the profile "sap"
...                 (Windows, SAP GUI open and logged in): uv run robotcode -p sap robot
Resource            ${EXECDIR}/resources/tasks/sap_tasks.resource
Resource            ${EXECDIR}/resources/assertions/sap_assertions.resource
Test Setup          Attach To SAP
Test Teardown       Detach From SAP
Test Tags           sap    hello-world    requires-sap


*** Test Cases ***
Own User Data Can Be Opened
    [Documentation]    The transaction SU3 shows your own user data (title "User" in an English SAP GUI).
    Open Transaction    SU3
    Window Title Should Include    User
