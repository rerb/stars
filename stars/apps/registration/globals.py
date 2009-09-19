EXEC_EMAIL_TEXT = """Congratulations!  {{ institution }} has successfully registered as a STARS Charter Participant through the Association for the Advancement of Sustainability in Higher Education (AASHE).

The primary STARS contact from your institution, listed below, is the person who provided your contact information to notify you about your institution's participation in STARS.  STARS, the Sustainability Tracking, Assessment & Rating System, is a tool to help guide institutions to become more sustainable. STARS requires the participation of many different individuals and departments on campus. As a result, executive level support is helpful to the STARS process. To learn more about the STARS Program we encourage you to connect with your campus liaison, check out the STARS website at www.aashe.org/stars, and email stars@aashe.org with any questions.

PRIMARY CONTACT:
{{ institution.contact_first_name }} {{ institution.contact_last_name }}
{{ institution.contact_title }}, {{ institution.contact_department }}
{{ institution.contact_email }}
"""

CONTACT_EMAIL_TEXT = """Thank you for registering {{ institution }} as a STARS Charter Participant! Your registration has been received and is being processed by AASHE. At this point, we encourage you to review the Technical Manual associated with the Early Release version of STARS 1.0 (www.aashe.org/stars). Please note that minor updates will be made to this document throughout the fall, such as providing additional examples and support text.  However, no changes will be made to the credits so you can immediately begin collecting the required data.  Access to the STARS online reporting tool will be available in January and you may begin submitting your collected data to STARS at that time. 
 
Please check the STARS website frequently at www.aashe.org/stars for updates and resources and email stars@aashe.org with any questions.

PAYMENT DETAILS:
{% ifequal payment.type "later" %}
    Amount Due: ${{ payment.amount }}
    
    Please send payment to "AASHE":
    213 1/2 N. Limestone
    Lexington, KY 40507
{% else %}
    We have successfully processed your payment!
    Credit Card Payment Ammount: ${{ payment.amount }}
{% endifequal %}
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
