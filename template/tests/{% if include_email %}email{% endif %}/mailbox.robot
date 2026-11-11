*** Settings ***
Documentation       Hello world for e-mails: waits for an e-mail and checks its content. Runs only with the
...                 profile "email" (enter the mailbox in resources/abilities/email_ability.resource):
...                 uv run robotcode -p email robot
Resource            ${EXECDIR}/resources/tasks/email_tasks.resource
Resource            ${EXECDIR}/resources/assertions/email_assertions.resource
Test Setup          Connect To Mailbox
Test Teardown       Disconnect From Mailbox
Test Tags           email    hello-world    requires-mailbox


*** Test Cases ***
Order Confirmation Has Arrived
    [Documentation]    An order confirmation from the shop has arrived and thanks for the order.
    ${email}    Wait For Email From    shop@example.com    Order confirmation
    Email Should Include Text    ${email}    Thank you for your order
