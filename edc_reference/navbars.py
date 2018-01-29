from edc_navbar import Navbar, NavbarItem, site_navbars


reference = Navbar(name='edc_reference')

reference.append_item(
    NavbarItem(name='reference',
               title='reference',
               label='reference',
               url_name='edc_reference:home_url'))

site_navbars.register(reference)
