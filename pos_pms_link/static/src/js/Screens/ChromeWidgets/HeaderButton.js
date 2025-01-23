/** @odoo-module **/
import Registries from 'point_of_sale.Registries';
import Chrome from 'point_of_sale.Chrome';


const PosPmsLinkChrome = (Chrome) =>
    class extends Chrome {
        get headerButtonIsShown() {
            var showButton = super.headerButtonIsShown;
            var close_session_allowed = this.env.pos.config.close_session_allowed
            return close_session_allowed ? close_session_allowed : showButton;
        }
    };

Registries.Component.extend(Chrome, PosPmsLinkChrome);