const BASE_DJANGO_URL = window.location.origin.match(/localhost/)
  ? 'http://localhost:8000'
  : window.location.origin;

const BASE_REACT_URL = window.location.origin.match(/localhost/)
  ? 'http://localhost:3000'
  : window.location.origin;

const API_ROOT = 'api';
export const DATES = `${BASE_DJANGO_URL}/${API_ROOT}/dates/`;
export const FILTER = `${BASE_DJANGO_URL}/${API_ROOT}/dates/filter_dates/`;
export const DELETE = `${BASE_DJANGO_URL}/${API_ROOT}/dates/delete_all_dates/`;

export const MONITOR =  `${BASE_REACT_URL}/`;