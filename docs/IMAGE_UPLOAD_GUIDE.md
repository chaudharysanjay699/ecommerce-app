# Image Upload Guide for Admin Categories & Products

## Overview

The backend now supports image uploads for both **categories** and **products**. Images are stored in the `uploads/` directory and served as static files.

## Features

✅ Upload images for categories and products  
✅ Automatic file validation (type, size)  
✅ Unique filename generation (prevents conflicts)  
✅ File size limit: 5MB  
✅ Supported formats: JPG, JPEG, PNG, GIF, WEBP  
✅ Automatic cleanup when deleting categories/products  

---

## Backend Implementation

### 1. File Upload Endpoints

#### Upload Category Image
```http
POST /api/v1/admin/categories/upload-image
Authorization: Bearer <admin_token>
Content-Type: multipart/form-data

Body:
  file: <binary image data>
```

**Response:**
```json
{
  "file_path": "uploads/categories/abc123def456.jpg",
  "file_url": "http://localhost:8000/uploads/categories/abc123def456.jpg",
  "filename": "my-category.jpg"
}
```

#### Upload Product Image
```http
POST /api/v1/admin/products/upload-image
Authorization: Bearer <admin_token>
Content-Type: multipart/form-data

Body:
  file: <binary image data>
```

**Response:**
```json
{
  "file_path": "uploads/products/xyz789abc123.png",
  "file_url": "http://localhost:8000/uploads/products/xyz789abc123.png",
  "filename": "my-product.png"
}
```

### 2. File Structure

```
ecom-copilot/
├── uploads/                    # Created automatically
│   ├── categories/            # Category images
│   │   └── abc123def456.jpg
│   └── products/              # Product images
│       └── xyz789abc123.png
└── app/
    ├── utils/
    │   └── file_upload.py     # Upload utilities
    └── main.py                # Static file serving
```

### 3. Database Schema

The `image_url` field stores the **full URL** to the uploaded image:

**Category Model:**
```python
image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
```

**Product Model:**
```python
image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
```

---

## Frontend Integration (React)

### Complete Workflow: Create Category with Image

```javascript
// adminService.js - Add this method
export const uploadCategoryImage = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/admin/categories/upload-image`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${getAuthToken()}`,
      // Don't set Content-Type - browser will set it with boundary
    },
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to upload image');
  }

  return response.json();
};

// Upload product image
export const uploadProductImage = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/admin/products/upload-image`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${getAuthToken()}`,
    },
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to upload image');
  }

  return response.json();
};
```

### Example: React Component for Category Creation

```jsx
// AdminCategoryForm.jsx
import React, { useState } from 'react';
import { uploadCategoryImage, createCategory } from '../services/adminService';

function AdminCategoryForm() {
  const [formData, setFormData] = useState({
    name: '',
    slug: '',
    type: 'grocery',
    description: '',
    image_url: '',
  });
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [uploading, setUploading] = useState(false);

  // Handle file selection
  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Validate file size (5MB)
      if (file.size > 5 * 1024 * 1024) {
        alert('File size must be less than 5MB');
        return;
      }

      // Validate file type
      const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
      if (!validTypes.includes(file.type)) {
        alert('Please select a valid image file (JPG, PNG, GIF, WEBP)');
        return;
      }

      setImageFile(file);
      
      // Show preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  // Upload image first, then create category
  const handleSubmit = async (e) => {
    e.preventDefault();
    setUploading(true);

    try {
      let imageUrl = formData.image_url;

      // Step 1: Upload image if selected
      if (imageFile) {
        const uploadResult = await uploadCategoryImage(imageFile);
        imageUrl = uploadResult.file_url;
      }

      // Step 2: Create category with image URL
      const categoryData = {
        ...formData,
        image_url: imageUrl,
      };

      await createCategory(categoryData);
      
      alert('Category created successfully!');
      // Reset form or redirect
      
    } catch (error) {
      console.error('Error:', error);
      alert(error.message || 'Failed to create category');
    } finally {
      setUploading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="category-form">
      <h2>Create Category</h2>

      <div className="form-group">
        <label>Name *</label>
        <input
          type="text"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          required
        />
      </div>

      <div className="form-group">
        <label>Slug *</label>
        <input
          type="text"
          value={formData.slug}
          onChange={(e) => setFormData({ ...formData, slug: e.target.value })}
          pattern="^[a-z0-9-]+$"
          title="Only lowercase letters, numbers, and hyphens"
          required
        />
      </div>

      <div className="form-group">
        <label>Type *</label>
        <select
          value={formData.type}
          onChange={(e) => setFormData({ ...formData, type: e.target.value })}
          required
        >
          <option value="grocery">Grocery</option>
          <option value="vegetable">Vegetable</option>
          <option value="basket">Basket</option>
          <option value="copy_pen">Copy & Pen</option>
        </select>
      </div>

      <div className="form-group">
        <label>Description</label>
        <textarea
          value={formData.description}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          rows="3"
        />
      </div>

      <div className="form-group">
        <label>Category Image</label>
        <input
          type="file"
          accept="image/jpeg,image/jpg,image/png,image/gif,image/webp"
          onChange={handleImageChange}
        />
        {imagePreview && (
          <div className="image-preview">
            <img src={imagePreview} alt="Preview" style={{ maxWidth: '200px', marginTop: '10px' }} />
          </div>
        )}
      </div>

      <button type="submit" disabled={uploading}>
        {uploading ? 'Creating...' : 'Create Category'}
      </button>
    </form>
  );
}

export default AdminCategoryForm;
```

### Simpler Approach: Direct Upload from Input

```jsx
// Simple file input component
function ImageUploadField({ label, onImageUrlChange }) {
  const [uploading, setUploading] = useState(false);
  const [preview, setPreview] = useState(null);

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);
    try {
      const result = await uploadCategoryImage(file);
      onImageUrlChange(result.file_url);
      setPreview(result.file_url);
      alert('Image uploaded successfully!');
    } catch (error) {
      alert('Failed to upload image: ' + error.message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div>
      <label>{label}</label>
      <input
        type="file"
        accept="image/*"
        onChange={handleUpload}
        disabled={uploading}
      />
      {uploading && <span>Uploading...</span>}
      {preview && <img src={preview} alt="Preview" style={{ width: '100px' }} />}
    </div>
  );
}

// Usage in form:
<ImageUploadField
  label="Category Image"
  onImageUrlChange={(url) => setFormData({ ...formData, image_url: url })}
/>
```

---

## Testing with cURL

### Upload Image
```bash
# Upload category image
curl -X POST "http://localhost:8000/api/v1/admin/categories/upload-image" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -F "file=@/path/to/image.jpg"

# Upload product image
curl -X POST "http://localhost:8000/api/v1/admin/products/upload-image" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -F "file=@/path/to/product.png"
```

### PowerShell Example
```powershell
$token = "YOUR_ADMIN_TOKEN"
$headers = @{"Authorization" = "Bearer $token"}

# Upload image
$form = @{
    file = Get-Item -Path "C:\path\to\image.jpg"
}

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/admin/categories/upload-image" `
  -Method Post `
  -Headers $headers `
  -Form $form
```

---

## Configuration Options

### Change Upload Settings

Edit `app/utils/file_upload.py`:

```python
# Maximum file size (default: 5MB)
MAX_FILE_SIZE = 10 * 1024 * 1024  # Change to 10MB

# Allowed extensions
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"}

# Upload directory
UPLOAD_DIR = Path("uploads")  # Or change to "static/uploads"
```

### Production Considerations

For production environments, consider:

1. **Use environment variables for base URL:**
```python
# In upload endpoint
base_url = os.getenv("BACKEND_URL", "http://localhost:8000")
file_url = f"{base_url}/{file_path.replace(chr(92), '/')}"
```

2. **Use cloud storage (S3, Azure Blob, etc.)** instead of local filesystem

3. **Add image optimization** (resize, compress) before saving

4. **Implement CDN** for serving uploaded images

---

## Error Handling

The upload endpoints validate:

✅ File type (must be image)  
✅ File extension (must be in allowed list)  
✅ File size (max 5MB by default)  
✅ Valid upload  

**Error Responses:**

```json
// Invalid file type
{
  "detail": "File type not allowed. Supported: .jpg, .jpeg, .png, .gif, .webp"
}

// File too large
{
  "detail": "File too large. Max size: 5MB"
}

// Not an image
{
  "detail": "File must be an image"
}
```

---

## Summary

1. **Upload image** using `/admin/categories/upload-image` or `/admin/products/upload-image`
2. **Get file_url** from response
3. **Use file_url** in `image_url` field when creating/updating category or product
4. Images are **automatically deleted** when you delete categories/products
5. Images are **served publicly** at `http://localhost:8000/uploads/...`

Images are now fully integrated into your ecommerce admin panel! 🎉
