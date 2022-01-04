# Interspire Email Marketer XML API for python

## Introduction

The Interspire Email Marketer XML API is a remotely accessible service API to allow Interspire Email
Marketer users to run many of the Interspire Email Marketer API functions using XML requests.
The Interspire Email Marketer XML API makes it possible to programmatically update and use your
system without needing to physically access it. As XML is a general purpose markup language you can
use it to communicate between your Java based applications to Interspire Email Marketer’s PHP
application base.
For example you could set your system up to automatically update contact lists, create and send email
campaigns, gather statistics and many other functions.

## Requirements

Python Package Requirements:

1. requests
2. xml

Authentication Requirements:
> An XML POST request with the details for the license to be generated should be sent to the ‘XML Path’
that you can find in the ‘User Accounts -> Edit User’ section of Interspire Email Marketer under the ‘User
Permissions’ tab. Make sure that you have ‘Enable the XML API’ checked and saved. The XML Path will
look similar to the following: `http://www.yourdomain.com/IEM/xml.php`
> The ‘username’ and ‘usertoken’ mentioned in the following examples can be found in this same section
under the title of ‘XML Username’ and ‘XML Token’ respectively

## Usage

1. Import API class: `from XMLApi_interspire import API`
2. Define API object: `api = API([http://www.yourdomain.com/IEM/xml.php], [username], [usertoken])`
3. Check if user is authenticated: `api.is_authenticated()`

### Possible Requests

1. Add Subscriber to a List
	details (Required)
	- emailaddress – The email address of the contact being added. (Required)
	- mailinglistid – The list that the contact is located within. (Required)
	- confirmed – Sets the confirmation status of the subscriber to confirmed or not (yes or y or true or 1) (Not required, default to unconfirmed)
	- format – The format of the email campaigns that this contact prefers to receive (html or h or text or t) (defaults to text)
	- customfields
		- item
    		- fieldid – The id of the custom field being added.
    		- value – The value to be added to this custom field.