import persons from './personData';

/**
 * Returns an array of mock person objects for the map.
 * If a count is provided and is less than the total mock data,
 * a slice is returned; otherwise the full mock dataset is used.
 *
 * @param {number} [count] - Desired number of mock people.
 * @returns {Array} Array of person objects.
 */
export function getMockPeople(count) {
  if (typeof count === 'number' && count > 0 && count < persons.length) {
    return persons.slice(0, count);
  }
  return persons;
}
