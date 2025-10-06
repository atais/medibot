// Import vendor libraries
import $ from 'jquery';
window.$ = $;
window.jQuery = $;

import * as bootstrap from 'bootstrap';
window.bootstrap = bootstrap;

require('bootstrap-datepicker');
require('bootstrap-select');
require('js-loading-overlay');
const noUiSlider = require('nouislider');
window.noUiSlider = noUiSlider;

import firebase from 'firebase/compat/app';
import 'firebase/compat/messaging';
window.firebase = firebase;

import './fcm.js';
import './medibot.js';
