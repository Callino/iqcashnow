To use this module, you need to:

#. Register for an account within https://www.iqcashnow.com/ (Go to Shop - Buy the odoo integration)
#. After Registriation you will get a key / secret pair
#. In Odoo - configure your payment acquirer with this data
#. Configure the new IQCashNow journal to use this payment acquirer


To configure this module, you need to:

* Register within https://www.iqcashnow.com/ for an account. You will receive a key / secret pair

* Go to Invoicing > Configuration > Journals - there is a new journal called "IQ Cashnow".
  Do configure this journal with your credentials from step 1.

.. figure:: https://raw.githubusercontent.com/OCA/mis-builder/10.0/mis_builder/static/description/ex_report_template.png
   :alt: Sample report template
   :width: 80 %
   :align: center

* Then in Accounting > Reports > MIS Reporting > MIS Reports you can create report instance by
  binding the templates to time periods, hence defining the columns of your reports.

.. figure:: https://raw.githubusercontent.com/OCA/mis-builder/10.0/mis_builder/static/description/ex_report_settings.png
   :alt: Sample report configuration
   :width: 80 %
   :align: center

* From the MIS Reports view, you can preview the report, add it to and Odoo dashboard,
  and export it to PDF or Excel.

.. figure:: https://raw.githubusercontent.com/OCA/mis-builder/10.0/mis_builder/static/description/ex_report_preview.png
   :alt: Sample preview
   :width: 80 %
   :align: center
