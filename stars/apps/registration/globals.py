EXEC_EMAIL_TEXT = """Dear {{ institution.executive_contact_title }} {{ institution.executive_contact_last_name }},
Congratulations!  {{ institution }} has successfully registered to participate in the Sustainability Tracking, Assessment & Rating System (STARS).  STARS is a tool to help guide colleges and universities toward sustainability.  

The STARS Liaison for {{ institution }}, listed below, provided your contact information to notify you about your institution's participation in STARS.  Since, many individuals and departments on campus will be involved in the STARS process, executive-level support will help make your institution's participation successful. 

To learn more about the STARS Program, visit www.aashe.org/stars or email stars@aashe.org with any questions. 

We're glad to have {{ institution }} as a STARS Charter Participant!

All the best, 

The STARS Team
stars@aashe.org

{{ institution }} STARS Liaison:
{{ institution.contact_first_name }} {{ institution.contact_last_name }}
{{ institution.contact_title }}, {{ institution.contact_department }}
{{ institution.contact_email }}
"""

RECEIPT_EMAIL_TEXT = """Thank you for registering as a STARS Charter Participant! 

Your registration has been received and is being processed by AASHE.  Your receipt is below.  

At this point, we encourage you to review the STARS 1.0 Early Release Technical Manual http://www.aashe.org/stars/early-release. Please note that minor updates will be made to this document before the January release, such as providing additional examples and support text.  However, no changes will be made to the credits, so you can immediately begin collecting the required information.  

Access to the STARS Reporting Tool will be available in January and you may begin submitting your collected data at that time.  To view a list of the reporting fields associated with each credit, please consult the Technical Manual.  
 
Please check the STARS website (www.aashe.org/stars) for updates and resources.  Feel free to email stars@aashe.org with any questions.

STARS REGISTRATION RECEIPT

FEE
${{ payment.amount }}

BILLING INFORMATION

Billed to:
{{ payment_dict.name_on_card }}
{{ payment_dict.billing_address }}
{{ payment_dict.billing_city }}, {{ payment_dict.billing_state }}, {{ payment_dict.billing_zipcode }}
{{ institution.contact_email }}

Total Fee ${{ payment.amount }}

Credit Card: [************{{ payment_dict.last_four }}]
Paid to AASHE
"""

PAY_LATER_EMAIL_TEXT="""Thank you for registering as a STARS Charter Participant! 

Your registration has been received and is being processed by AASHE.  Your receipt is below.  

At this point, we encourage you to review the STARS 1.0 Early Release Technical Manual (http://www.aashe.org/stars/early-release). Please note that minor updates, such as providing additional examples and support text, will be made to this document before the January release.  However, no changes will be made to the credits, so you can immediately begin collecting the required information.  

Access to the STARS Reporting Tool will be available in January and you may begin submitting your collected data at that time.  To view a list of the reporting fields associated with each credit, please consult the Technical Manual.  

Please check the STARS website (www.aashe.org/stars) for updates and resources and email stars@aashe.org with any questions.
 
STARS REGISTRATION PAYMENT

FEE
${{ payment.amount }} 

BILLING INFORMATION

You have selected to pay for your STARS registration by check. Please mail a check payable to AASHE in the amount of ${{ payment.amount }} to:
 
AASHE
213 1/2 N. Limestone Street
Lexington, Kentucky 40507
"""

CYBERSOURCE_RESPONSE_DICT = {
    '100' : 'Successful transaction.',
    '101' : 'The request is missing one or more required fields.',
    '102' : 'One or more fields in the request contains invalid data.',
    '104' : 'The merchantReferenceCode sent with this authorization request matches the merchantReferenceCode of another authorization request that you sent in the last 15 minutes.',
    '150' : 'Error: General system failure. ',
    '151' : 'Error: The request was received but there was a server timeout. This error does not include timeouts between the client and the server.',
    '152' : 'Error: The request was received, but a service did not finish running in time.',
    '201' : 'The issuing bank has questions about the request. You do not receive an authorization code in the reply message, but you might receive one verbally by calling the processor.',
    '202' : 'Expired card. You might also receive this if the expiration date you provided does not match the date the issuing bank has on file.',
    '203' : 'General decline of the card. No other information provided by the issuing bank.',
    '204' : 'Insufficient funds in the account.',
    '205' : 'Stolen or lost card.',
    '207' : 'Issuing bank unavailable.',
    '208' : 'Inactive card or card not authorized for card-not-present transactions.',
    '210' : 'The card has reached the credit limit. ',
    '211' : 'Invalid card verification number.',
    '221' : 'The customer matched an entry on the processor\'s negative file.',
    '231' : 'Invalid card number.',
    '232' : 'The card type is not accepted by the payment processor.',
    '233' : 'General decline by the processor.',
    '234' : 'There is a problem with your CyberSource merchant configuration.',
    '235' : 'The requested amount exceeds the originally authorized amount. Occurs, for example, if you try to capture an amount larger than the original authorization amount. This reason code only applies if you are processing a capture through the API.',
    '236' : 'Processor Failure',
    '238' : 'The authorization has already been captured. This reason code only applies if you are processing a capture through the API.',
    '239' : 'The requested transaction amount must match the previous transaction amount. This reason code only applies if you are processing a capture or credit through the API.',
    '240' : 'The card type sent is invalid or does not correlate with the credit card number.',
    '241' : 'The request ID is invalid. This reason code only applies when you are processing a capture or credit through the API.',
    '242' : 'You requested a capture through the API, but there is no corresponding, unused authorization record. Occurs if there was not a previously successful authorization request or if the previously successful authorization has already been used by another capture request. This reason code only applies when you are processing a capture through the API.',
    '243' : 'The transaction has already been settled or reversed.',
    '246' : 'The capture or credit is not voidable because the capture or credit information has already been submitted to your processor. Or, you requested a void for a type of transaction that cannot be voided. This reason code applies only if you are processing a void through the API.',
    '247' : 'You requested a credit for a capture that was previously voided. This reason code applies only if you are processing a void through the API.',
    '250' : 'Error: The request was received, but there was a timeout at the payment processor.',
    '520' : 'The authorization request was approved by the issuing bank but declined by CyberSource based on your Smart Authorization settings.',
}
