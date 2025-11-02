export default async function handler(request, response) {
  return response.status(200).json({ status: 'OK', timestamp: new Date().toISOString() });
}
