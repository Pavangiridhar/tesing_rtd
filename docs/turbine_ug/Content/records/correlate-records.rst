Correlate Records
=================

You can correlate records within a single application within Swimlane
Turbine. Upon ingestion of new application records, Turbine compares the
new record to previous records that have correlation keys.

Record Correlation executes two tasks:

-  Compares correlation key fields across records in a single
   application, looking for configurable similarities.
-  Updates a correlation field in the associated records.

The following correlation field types have the below default
configurations and will be compared with the matching preferences on the
Settings tab:

+----------------------------------+----------------------------------+
| **Correlation Field Type**       | **Value and Default              |
|                                  | Information**                    |
+==================================+==================================+
| IPv4 public addresses            | Plus or minus 255 values.        |
|                                  | Example: 10.10.11.0 –            |
|                                  | 10.10.10.254 = 2                 |
+----------------------------------+----------------------------------+
| IPv4 private addresses           | Exact match between addresses    |
+----------------------------------+----------------------------------+
| IPv6 public addresses            | Within 65535 values              |
+----------------------------------+----------------------------------+
| Domains, URLs, file names, and   | Has a threshold of 90%           |
| email addresses                  | similarity, calculated via       |
|                                  | “lengthwise Levenshtein” of less |
|                                  | than 1 character substitution    |
|                                  | per 10 characters of string      |
|                                  | length                           |
+----------------------------------+----------------------------------+
| List elements                    | Lists of raw text strings as     |
|                                  | well as ipv4_public,             |
|                                  | ipv6_public, domain, url, email, |
|                                  | md5, sha1, sha256, ssdeep,       |
|                                  | filename list values.            |
+----------------------------------+----------------------------------+
| File attachments                 | Fuzzy hash similarity greater    |
|                                  | than or equal to 90%             |
+----------------------------------+----------------------------------+

Configure Record Correlations
-----------------------------

To configure record correlations, follow the steps below.

Let's start by creating an application.

#. From the Navigation menu, click **APPLICATIONS & APPLETS**.

#. | Click the **plus** icon, and then click **Create a new
     application**.
   | |image1|

3. On Create Application, complete the **Name** field. You can click the
   GENERAL, ADMINISTRATION, RECORDS, or WORKSPACE tabs to add
   information or use the **Next** and **Prev** buttons to move through
   the tabs.

4. | Click **+Create**.
   | |image2|

6. Click and drag the following field types into the FORM LAYOUT section
   to start building your application: **Text**, **IP**, **URL**, and
   **Correlation**.

#. To setup correlation settings, click **Manage correlation settings**
   hyperlink.
   |image3|

#. For details about how record correlation executes and default values
   for specific Correlation field types, click the **Documentation**
   tab.
   |image4|

#. | After you set the Matching Preferences, click the **Correlation
     Field** drop-down arrow and select a field type.
   | |image5|

   **Tip:** Click **Add a Correlation Field** to create another
   drop-down list.

#. | Next, click the **Expected Value Type** drop-down arrow and select
     a value type.
   | |image6|

#. To set a filter that narrows your correlation results by a specific
   field, identify that field under the Filter heading.

#. You can also prompt a playbook run upon correlation. Identify the
   playbook under the Correlation Action heading of the dialog.

#. To save record correlation settings, click **Apply**.

.. |image1| image:: ../Resources/Images/create-a-new-application-button.png
.. |image2| image:: ../Resources/Images/create-application-window-alerts.png
.. |image3| image:: ../Resources/Images/manage-correlation-settings-hyperlink.png
.. |image4| image:: ../Resources/Images/record-correlation-documentation-tab.png
.. |image5| image:: ../Resources/Images/correlation-field-dropdown.png
.. |image6| image:: ../Resources/Images/expected-value-type.png
