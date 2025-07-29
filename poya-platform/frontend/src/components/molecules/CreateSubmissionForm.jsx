import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  Typography,
  Alert,
  LinearProgress,
} from '@mui/material';
import { createSubmission, clearError, clearSuccess } from '../../store/submissionSlice';

const SUBMISSION_TYPES = [
  { value: 'REPORT', label: 'Report' },
  { value: 'PROBLEM', label: 'Problem' },
  { value: 'SUGGESTION', label: 'Suggestion' },
];

const IMPORTANCE_LEVELS = [
  { value: 'HIGH', label: 'High' },
  { value: 'MEDIUM', label: 'Medium' },
  { value: 'LOW', label: 'Low' },
];

const CreateSubmissionForm = ({ open, onClose }) => {
  const dispatch = useDispatch();
  const { loading, error, success } = useSelector((state) => state.submissions);
  const [formData, setFormData] = useState({
    title: '',
    type: '',
    description: '',
    importance_level: '',
    assignee_id: null,
  });

  useEffect(() => {
    if (success) {
      setTimeout(() => {
        dispatch(clearSuccess());
        onClose();
      }, 1500);
    }
  }, [success, dispatch, onClose]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    await dispatch(createSubmission(formData));
  };

  const handleClose = () => {
    setFormData({
      title: '',
      type: '',
      description: '',
      importance_level: '',
      assignee_id: null,
    });
    dispatch(clearError());
    dispatch(clearSuccess());
    onClose();
  };

  const isValid = formData.title && 
                 formData.type && 
                 formData.description && 
                 formData.importance_level;

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>Create New Submission</DialogTitle>
      <form onSubmit={handleSubmit}>
        <DialogContent>
          {loading && <LinearProgress />}
          
          <Box display="flex" flexDirection="column" gap={2} mt={1}>
            {error && (
              <Alert severity="error" onClose={() => dispatch(clearError())}>
                {error}
              </Alert>
            )}
            
            {success && (
              <Alert severity="success">{success}</Alert>
            )}

            <TextField
              name="title"
              label="Title"
              value={formData.title}
              onChange={handleChange}
              fullWidth
              required
            />

            <FormControl fullWidth required>
              <InputLabel>Type</InputLabel>
              <Select
                name="type"
                value={formData.type}
                onChange={handleChange}
                label="Type"
              >
                {SUBMISSION_TYPES.map((type) => (
                  <MenuItem key={type.value} value={type.value}>
                    {type.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <FormControl fullWidth required>
              <InputLabel>Importance Level</InputLabel>
              <Select
                name="importance_level"
                value={formData.importance_level}
                onChange={handleChange}
                label="Importance Level"
              >
                {IMPORTANCE_LEVELS.map((level) => (
                  <MenuItem key={level.value} value={level.value}>
                    {level.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <TextField
              name="description"
              label="Description"
              value={formData.description}
              onChange={handleChange}
              multiline
              rows={4}
              fullWidth
              required
            />

            {(formData.importance_level === 'HIGH' || formData.importance_level === 'MEDIUM') && (
              <Typography color="text.secondary" variant="body2">
                Note: A task will be automatically created for this submission.
              </Typography>
            )}
          </Box>
        </DialogContent>

        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          <Button 
            type="submit" 
            variant="contained" 
            color="primary"
            disabled={!isValid || loading}
          >
            Submit
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default CreateSubmissionForm;
