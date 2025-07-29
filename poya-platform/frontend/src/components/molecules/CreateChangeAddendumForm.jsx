import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Box,
  Typography,
  LinearProgress,
  Alert,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  IconButton
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  AttachFile as AttachFileIcon,
  Delete as DeleteIcon
} from '@mui/icons-material';
import { createChangeAddendum, clearSuccess, clearError } from '../store/changeRequestSlice';

const CreateChangeAddendumForm = ({ open, onClose, requestId }) => {
  const dispatch = useDispatch();
  const { loading, error, success } = useSelector((state) => state.changeRequest);
  
  const [description, setDescription] = useState('');
  const [impactAnalysis, setImpactAnalysis] = useState('');
  const [technicalJustification, setTechnicalJustification] = useState('');
  const [selectedFiles, setSelectedFiles] = useState([]);

  const handleFileSelect = (event) => {
    const files = Array.from(event.target.files);
    setSelectedFiles([...selectedFiles, ...files]);
  };

  const handleRemoveFile = (index) => {
    setSelectedFiles(selectedFiles.filter((_, i) => i !== index));
  };

  const handleSubmit = async () => {
    await dispatch(createChangeAddendum({
      originalRequestId: requestId,
      data: {
        description,
        impactAnalysis,
        technicalJustification
      },
      files: selectedFiles
    }));
  };

  const handleClose = () => {
    setDescription('');
    setImpactAnalysis('');
    setTechnicalJustification('');
    setSelectedFiles([]);
    dispatch(clearError());
    dispatch(clearSuccess());
    onClose();
  };

  // Close dialog on success
  React.useEffect(() => {
    if (success) {
      handleClose();
    }
  }, [success]);

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>Request Change Addendum</DialogTitle>
      <DialogContent>
        <Box mt={2} display="flex" flexDirection="column" gap={3}>
          {error && (
            <Alert severity="error" onClose={() => dispatch(clearError())}>
              {error.message || 'An error occurred'}
            </Alert>
          )}

          <TextField
            label="Description of Changes"
            multiline
            rows={4}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            fullWidth
            required
          />

          <TextField
            label="Impact Analysis"
            multiline
            rows={4}
            value={impactAnalysis}
            onChange={(e) => setImpactAnalysis(e.target.value)}
            fullWidth
            required
            helperText="Describe the impact of these changes on cost, schedule, and quality"
          />

          <TextField
            label="Technical Justification"
            multiline
            rows={4}
            value={technicalJustification}
            onChange={(e) => setTechnicalJustification(e.target.value)}
            fullWidth
            required
            helperText="Provide technical reasons for requesting these changes"
          />

          <Box>
            <input
              type="file"
              multiple
              onChange={handleFileSelect}
              style={{ display: 'none' }}
              id="file-upload-input"
            />
            <label htmlFor="file-upload-input">
              <Button
                variant="outlined"
                component="span"
                startIcon={<UploadIcon />}
              >
                Upload Files
              </Button>
            </label>

            {selectedFiles.length > 0 && (
              <List>
                {selectedFiles.map((file, index) => (
                  <ListItem
                    key={index}
                    secondaryAction={
                      <IconButton
                        edge="end"
                        onClick={() => handleRemoveFile(index)}
                      >
                        <DeleteIcon />
                      </IconButton>
                    }
                  >
                    <ListItemIcon>
                      <AttachFileIcon />
                    </ListItemIcon>
                    <ListItemText
                      primary={file.name}
                      secondary={`${(file.size / 1024 / 1024).toFixed(2)} MB`}
                    />
                  </ListItem>
                ))}
              </List>
            )}
          </Box>
        </Box>

        {loading && (
          <Box mt={2}>
            <LinearProgress />
          </Box>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose} disabled={loading}>
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          color="primary"
          variant="contained"
          disabled={loading || !description || !impactAnalysis || !technicalJustification}
        >
          Submit Request
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default CreateChangeAddendumForm;
