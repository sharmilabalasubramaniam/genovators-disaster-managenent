const persons = [
  {
    id: 'P001',
    name: 'John Doe',
    photo: 'https://via.placeholder.com/80?text=John',
    latitude: 37.775,
    longitude: -122.418,
    status: 'Identified',
    identifiedAt: new Date().toISOString(),
    locationName: 'San Francisco Downtown'
  },
  {
    id: 'P002',
    name: 'Jane Smith',
    photo: '', // No photo – will fallback to placeholder
    latitude: 37.776,
    longitude: -122.419,
    status: 'Missing',
    identifiedAt: new Date().toISOString(),
    locationName: 'Golden Gate Park'
  },
  {
    id: 'P003',
    name: 'Bob Lee',
    photo: 'https://via.placeholder.com/80?text=Bob',
    latitude: 37.777,
    longitude: -122.42,
    status: 'Reunited',
    identifiedAt: new Date().toISOString(),
    locationName: 'Market Street'
  }
];

export default persons;
