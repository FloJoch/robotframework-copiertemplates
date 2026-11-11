*** Settings ***
Documentation       Hello world for images and PDFs: comparison with reference files from data/reference.
...                 The example compares the reference with itself - replace it with real documents.
Resource            ${EXECDIR}/resources/tasks/doctest_tasks.resource
Resource            ${EXECDIR}/resources/assertions/doctest_assertions.resource
Test Tags           documents    hello-world


*** Test Cases ***
Image Matches The Reference
    [Documentation]    The image looks like the reference.
    ${image}    Get Document    example.png
    Image Should Match Reference    ${image}    example.png

PDF Matches The Reference And Includes The Text
    [Documentation]    The PDF looks like the reference and includes the expected text.
    ${pdf}    Get Document    example.pdf
    PDF Should Match Reference    ${pdf}    example.pdf
    PDF Should Include Texts    ${pdf}    Hallo Robot Framework
