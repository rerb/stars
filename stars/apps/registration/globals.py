EXEC_EMAIL_TEXT = """{% autoescape off %}Dear {{ institution.executive_contact_title }} {{ institution.executive_contact_last_name }},
Congratulations!  {{ institution }} has successfully registered to participate in the Sustainability Tracking, Assessment & Rating System (STARS).  STARS is a tool to help guide colleges and universities toward sustainability.  

The STARS Liaison for {{ institution }}, listed below, provided your contact information to notify you about your institution's participation in STARS.  Since many individuals and departments on campus will be involved in the STARS process, executive-level support will help make your institution's participation successful.

To learn more about the STARS Program, visit http://stars.aashe.org/ or email stars@aashe.org with any questions. 

We're glad to have {{ institution }} as a STARS Participant!

All the best, 

The STARS Team
stars@aashe.org

{{ institution }} STARS Liaison:
{{ institution.contact_first_name }} {{ institution.contact_last_name }}
{{ institution.contact_title }}, {{ institution.contact_department }}
{{ institution.contact_email }}
{% endautoescape %}
"""

RECEIPT_EMAIL_TEXT = """{% autoescape off %}Thank you for registering as a STARS Participant! 

Your registration has been received and is being processed by AASHE.  Your receipt is below.  

You may now access the STARS Reporting Tool.  For instructions on getting started with the Reporting Tool, visit: http://stars.aashe.org/pages/help/3900/

To view details about each credit, including the reporting fields associated with each credit, please consult the STARS 1.0 Technical Manual (http://stars.aashe.org/pages/about/3993/).
 
Please check the STARS website (http://stars.aashe.org/) for updates and resources.  Feel free to email stars@aashe.org with any questions.

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
{% endautoescape %}
"""

PAY_LATER_EMAIL_TEXT="""{% autoescape off %}Thank you for registering as a STARS Participant! 

Your registration has been received and is being processed by AASHE.  Your receipt is below.  

Access to the STARS Reporting Tool will be available when we receive your registration payment.

For details about each credit, including a list of the reporting fields associated with each credit, please consult the STARS 1.0 Technical Manual (http://stars.aashe.org/pages/about/3993/).

Please check the STARS website (http://stars.aashe.org) for updates and resources and email stars@aashe.org with any questions.
 
STARS REGISTRATION PAYMENT

FEE
${{ payment.amount }} 

BILLING INFORMATION

You selected the "pay later" option for your STARS registration. Payment is due w/in the next 4 weeks. Please note, although your institution has successfully registered for the STARS program, the institution name will not be listed on the STARS website until payment is received.

Please mail a check payable to AASHE in the amount of ${{ payment.amount }} to:
 
AASHE
213 1/2 N. Limestone Street
Lexington, Kentucky 40507

Or, to pay by Credit Card, please call our main office at:

(859) 258-2551

{% endautoescape %}
"""

PAY_LATER_REMINDER_TEXT ="""{% autoescape off %}This is a friendly reminder that your STARS registration fee is ${{ payment.amount }} .

During the registration process you indicated that you would "pay later".

If you would like to pay by check, please submit payment to AASHE at:

AASHE
213 1/2 N Limestone St
Lexington, KY 40507

If you would like to pay by Credit Card, please call our main office at:

(859) 258-2551


Thank you!

The STARS Team
stars@aashe.org
http://stars.aashe.org
{% endautoescape %}
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
