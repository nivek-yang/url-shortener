import Alpine from 'alpinejs';
import { indexShortener } from './indexShortener.js';
import { shortenerForm } from './shortenerForm.js';

Alpine.data('shortenerForm', shortenerForm);
Alpine.data('indexShortener', indexShortener);

Alpine.start();
