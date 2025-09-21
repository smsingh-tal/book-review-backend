# Storage Service API Documentation

## Overview

The Storage Service provides endpoints for handling file uploads, specifically for profile pictures and book covers. The service supports JPG and PNG formats with automatic image optimization.

## Base URL

```
http://localhost:8000
```

## Authentication

All endpoints except `GET /storage/{file_path}` require authentication. Include the JWT token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

## Endpoints

### Upload File

Upload an image file to the server.

```
POST /storage/upload
```

#### Request

- Method: `POST`
- Content-Type: `multipart/form-data`

##### Parameters

| Name     | Type   | In     | Required | Description                                     |
|----------|--------|--------|----------|-------------------------------------------------|
| file     | File   | form   | Yes      | The file to upload (JPG or PNG)                |
| subdir   | String | query  | No       | Subdirectory to store the file in (e.g., "profiles" or "books") |

##### Constraints

- Maximum file size: 5MB
- Supported formats: JPG, PNG
- Files will be automatically optimized for storage

#### Response

##### Success (200 OK)
```json
{
    "file_path": "string"
}
```

The `file_path` can be used to construct the full URL to access the file:
`http://localhost:8000/uploads/{file_path}`

##### Errors

| Status Code | Description           | Response Body                                    |
|-------------|--------------------|------------------------------------------------|
| 400         | Invalid format     | `{"detail": "File format not supported. Only JPG and PNG are allowed."}` |
| 400         | File too large     | `{"detail": "File size exceeds maximum limit of 5MB"}` |
| 401         | Unauthorized       | `{"detail": "Not authenticated"}` |
| 500         | Server error       | `{"detail": "Error saving file: <error_message>"}` |

### Get File

Retrieve a previously uploaded file.

```
GET /storage/{file_path}
```

#### Request

- Method: `GET`
- No authentication required

##### Parameters

| Name      | Type   | In     | Required | Description                    |
|-----------|--------|--------|----------|--------------------------------|
| file_path | String | path   | Yes      | Path to the file to retrieve   |

#### Response

##### Success (200 OK)
- Content-Type: `image/jpeg` or `image/png`
- Body: The file content

##### Errors

| Status Code | Description     | Response Body                     |
|-------------|----------------|----------------------------------|
| 404         | Not found      | `{"detail": "File not found"}`   |

### Delete File

Delete a previously uploaded file.

```
DELETE /storage/{file_path}
```

#### Request

- Method: `DELETE`
- Requires authentication

##### Parameters

| Name      | Type   | In     | Required | Description                  |
|-----------|--------|--------|----------|------------------------------|
| file_path | String | path   | Yes      | Path to the file to delete   |

#### Response

##### Success (200 OK)
```json
{
    "message": "File deleted successfully"
}
```

##### Errors

| Status Code | Description     | Response Body                                    |
|-------------|----------------|------------------------------------------------|
| 401         | Unauthorized   | `{"detail": "Not authenticated"}`               |
| 404         | Not found      | `{"detail": "File not found"}`                 |
| 500         | Server error   | `{"detail": "Error deleting file: <error_message>"}` |

## Example Usage (React + Axios)

```typescript
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

// Upload a file
async function uploadFile(file: File, subdir?: string) {
  const formData = new FormData();
  formData.append('file', file);
  
  const url = subdir 
    ? `${API_BASE_URL}/storage/upload?subdir=${subdir}`
    : `${API_BASE_URL}/storage/upload`;
    
  const response = await axios.post(url, formData, {
    headers: {
      'Authorization': `Bearer ${yourAuthToken}`,
      'Content-Type': 'multipart/form-data'
    }
  });
  
  return response.data.file_path;
}

// Get file URL
function getFileUrl(filePath: string) {
  return `${API_BASE_URL}/uploads/${filePath}`;
}

// Delete a file
async function deleteFile(filePath: string) {
  await axios.delete(`${API_BASE_URL}/storage/${filePath}`, {
    headers: {
      'Authorization': `Bearer ${yourAuthToken}`
    }
  });
}

// Example usage
try {
  // Upload profile picture
  const file = event.target.files[0];
  const filePath = await uploadFile(file, 'profiles');
  
  // Get URL for display
  const imageUrl = getFileUrl(filePath);
  
  // Later, delete the file if needed
  await deleteFile(filePath);
} catch (error) {
  console.error('Error:', error.response?.data?.detail || error.message);
}
```

## Best Practices

1. **File Size**: Always validate file size on the frontend before uploading to avoid unnecessary network requests.
2. **File Type**: Check file type on the frontend using the file's MIME type.
3. **Error Handling**: Implement proper error handling for all API calls.
4. **Loading States**: Show appropriate loading states during file uploads.
5. **Image Preview**: Consider implementing client-side image preview before upload.

## Rate Limiting

- No specific rate limits are currently implemented.
- Consider implementing reasonable limits in production.

## Notes

- Files are stored in the `uploads` directory on the server.
- File names are automatically generated using UUIDs to prevent conflicts.
- Images are automatically optimized to reduce storage size while maintaining quality.
- The service supports organizing files in subdirectories (e.g., "profiles" for profile pictures, "books" for book covers).
