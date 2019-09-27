import EThingUI from 'ething-ui'
import WGoogleCalendar from './components/WGoogleCalendar'
import WGoogleNews from './components/WGoogleNews'
import GoogleAccounts from './components/GoogleAccounts'
import GoogleUserForm from './components/GoogleUserForm'


EThingUI.extend('plugins/google', {

    components (plugin) {
      return {
        'accounts': {
            component: GoogleAccounts,
            title: 'accounts',
        }
      }
    },

})

EThingUI.form.registerForm(GoogleUserForm)


EThingUI.extend('resources/GoogleCalendar', {

    components (resource) {
      return {
        'default': {
            component: 'widget',
            icon: 'mdi-calendar',
            title: 'Calendar',
            attributes () {
              return {
                widget: 'default',
                height: '400px'
              }
            }
        }
      }
    },

    widgets (resource) {
      return {
        'default': {
            component: WGoogleCalendar,
            title: 'Calendar',
            description: 'display the events',
            minHeight: 250,
            zIndex: 100
        }
      }
    },

})

EThingUI.registerWidget('GoogleNews', {
  component: WGoogleNews,
  title: 'Google news widget',
  description: 'display local news',
  minHeight: 120,
  schema: {
    properties: {
      language: {
        $labels: ["Afrikaans","Albanian","Amharic","Arabic","Azerbaijani","Basque","Belarusian","Bengali","Bihari","Bosnian","Bulgarian","Catalan","Chinese (Simplified)","Chinese (Traditional)","Croatian","Czech","Danish","Dutch","English","Esperanto","Estonian","Faroese","Finnish","French","Frisian","Galician","Georgian","German","Greek","Gujarati","Hebrew","Hindi","Hungarian","Icelandic","Indonesian","Interlingua","Irish","Italian","Japanese","Javanese","Kannada","Korean","Latin","Latvian","Lithuanian","Macedonian","Malay","Malayam","Maltese","Marathi","Nepali","Norwegian","Norwegian (Nynorsk)","Occitan","Persian","Polish","Portuguese (Brazil)","Portuguese (Portugal)","Punjabi","Romanian","Russian","Scots Gaelic","Serbian","Sinhalese","Slovak","Slovenian","Spanish","Sudanese","Swahili","Swedish","Tagalog","Tamil","Telugu","Thai","Tigrinya","Turkish","Ukrainian","Urdu","Uzbek","Vietnamese","Welsh","Xhosa","Zulu"],
        enum: ["af","sq","sm","ar","az","eu","be","bn","bh","bs","bg","ca","zh-CN","zh-TW","hr","cs","da","nl","en","eo","et","fo","fi","fr","fy","gl","ka","de","el","gu","iw","hi","hu","is","id","ia","ga","it","ja","jw","kn","ko","la","lv","lt","mk","ms","ml","mt","mr","ne","no","nn","oc","fa","pl","pt-BR","pt-PT","pa","ro","ru","gd","sr","si","sk","sl","es","su","sw","sv","tl","ta","te","th","ti","tr","uk","ur","uz","vi","cy","xh","zu"],
        default: 'en'
      },
      country: {
        $labels: ["Afghanistan","Albania","Algeria","American Samoa","Andorra","Angola","Anguilla","Antarctica","Antigua and Barbuda","Argentina","Armenia","Aruba","Australia","Austria","Azerbaijan","Bahamas","Bahrain","Bangladesh","Barbados","Belarus","Belgium","Belize","Benin","Bermuda","Bhutan","Bolivia","Bosnia and Herzegovina","Botswana","Bouvet Island","Brazil","British Indian Ocean Territory","Brunei Darussalam","Bulgaria","Burkina Faso","Burundi","Cambodia","Cameroon","Canada","Cape Verde","Cayman Islands","Central African Republic","Chad","Chile","China","Christmas Island","Cocos (Keeling) Islands","Colombia","Comoros","Congo","Congo, the Democratic Republic of the","Cook Islands","Costa Rica","Cote D'ivoire","Croatia","Cuba","Cyprus","Czech Republic","Denmark","Djibouti","Dominica","Dominican Republic","Ecuador","Egypt","El Salvador","Equatorial Guinea","Eritrea","Estonia","Ethiopia","Falkland Islands (Malvinas)","Faroe Islands","Fiji","Finland","France","French Guiana","French Polynesia","French Southern Territories","Gabon","Gambia","Georgia","Germany","Ghana","Gibraltar","Greece","Greenland","Grenada","Guadeloupe","Guam","Guatemala","Guinea","Guinea-Bissau","Guyana","Haiti","Heard Island and Mcdonald Islands","Holy See (Vatican City State)","Honduras","Hong Kong","Hungary","Iceland","India","Indonesia","Iran, Islamic Republic of","Iraq","Ireland","Israel","Italy","Jamaica","Japan","Jordan","Kazakhstan","Kenya","Kiribati","Korea, Democratic People's Republic of","Korea, Republic of","Kuwait","Kyrgyzstan","Lao People's Democratic Republic","Latvia","Lebanon","Lesotho","Liberia","Libyan Arab Jamahiriya","Liechtenstein","Lithuania","Luxembourg","Macao","Macedonia, the Former Yugosalv Republic of","Madagascar","Malawi","Malaysia","Maldives","Mali","Malta","Marshall Islands","Martinique","Mauritania","Mauritius","Mayotte","Mexico","Micronesia, Federated States of","Moldova, Republic of","Monaco","Mongolia","Montserrat","Morocco","Mozambique","Myanmar","Namibia","Nauru","Nepal","Netherlands","Netherlands Antilles","New Caledonia","New Zealand","Nicaragua","Niger","Nigeria","Niue","Norfolk Island","Northern Mariana Islands","Norway","Oman","Pakistan","Palau","Palestinian Territory, Occupied","Panama","Papua New Guinea","Paraguay","Peru","Philippines","Pitcairn","Poland","Portugal","Puerto Rico","Qatar","Reunion","Romania","Russian Federation","Rwanda","Saint Helena","Saint Kitts and Nevis","Saint Lucia","Saint Pierre and Miquelon","Saint Vincent and the Grenadines","Samoa","San Marino","Sao Tome and Principe","Saudi Arabia","Senegal","Serbia and Montenegro","Seychelles","Sierra Leone","Singapore","Slovakia","Slovenia","Solomon Islands","Somalia","South Africa","South Georgia and the South Sandwich Islands","Spain","Sri Lanka","Sudan","Suriname","Svalbard and Jan Mayen","Swaziland","Sweden","Switzerland","Syrian Arab Republic","Taiwan, Province of China","Tajikistan","Tanzania, United Republic of","Thailand","Timor-Leste","Togo","Tokelau","Tonga","Trinidad and Tobago","Tunisia","Turkey","Turkmenistan","Turks and Caicos Islands","Tuvalu","Uganda","Ukraine","United Arab Emirates","United Kingdom","United States","United States Minor Outlying Islands","Uruguay","Uzbekistan","Vanuatu","Venezuela","Viet Nam","Virgin Islands, British","Virgin Islands, U.S.","Wallis and Futuna","Western Sahara","Yemen","Zambia","Zimbabwe"],
        enum: ["af","al","dz","as","ad","ao","ai","aq","ag","ar","am","aw","au","at","az","bs","bh","bd","bb","by","be","bz","bj","bm","bt","bo","ba","bw","bv","br","io","bn","bg","bf","bi","kh","cm","ca","cv","ky","cf","td","cl","cn","cx","cc","co","km","cg","cd","ck","cr","ci","hr","cu","cy","cz","dk","dj","dm","do","ec","eg","sv","gq","er","ee","et","fk","fo","fj","fi","fr","gf","pf","tf","ga","gm","ge","de","gh","gi","gr","gl","gd","gp","gu","gt","gn","gw","gy","ht","hm","va","hn","hk","hu","is","in","id","ir","iq","ie","il","it","jm","jp","jo","kz","ke","ki","kp","kr","kw","kg","la","lv","lb","ls","lr","ly","li","lt","lu","mo","mk","mg","mw","my","mv","ml","mt","mh","mq","mr","mu","yt","mx","fm","md","mc","mn","ms","ma","mz","mm","na","nr","np","nl","an","nc","nz","ni","ne","ng","nu","nf","mp","no","om","pk","pw","ps","pa","pg","py","pe","ph","pn","pl","pt","pr","qa","re","ro","ru","rw","sh","kn","lc","pm","vc","ws","sm","st","sa","sn","cs","sc","sl","sg","sk","si","sb","so","za","gs","es","lk","sd","sr","sj","sz","se","ch","sy","tw","tj","tz","th","tl","tg","tk","to","tt","tn","tr","tm","tc","tv","ug","ua","ae","uk","us","um","uy","uz","vu","ve","vn","vg","vi","wf","eh","ye","zm","zw"],
        default: 'us'
      }
    }
  }
})
