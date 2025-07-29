import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
} from '@mui/material';
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker';
import { useDispatch, useSelector } from 'react-redux';
import { updateTask } from '../../store/taskSlice';

const priorityOptions = [
  { value: 1, label: 'Low' },
  { value: 2, label: 'Medium' },
  { value: 3, label: 'High' },
  { value: 4, label: 'Urgent' },
];

const EditTaskModal = ({ task, open, onClose }) => {
  const dispatch = useDispatch();
  const users = useSelector((state) => state.auth.users);
  
  const [formData, setFormData] = useState({
    title: task?.title || '',
    description: task?.description || '',
    priority: task?.priority || 2,
    assignee_id: task?.assignee_id || '',
    due_date: task?.due_date ? new Date(task.due_date) : null,
  });

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleDateChange = (date) => {
    setFormData((prev) => ({
      ...prev,
      due_date: date,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      await dispatch(updateTask({ taskId: task.id, taskData: formData })).unwrap();
      onClose();
    } catch (error) {
      console.error('Failed to update task:', error);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <form onSubmit={handleSubmit}>
        <DialogTitle>Edit Task</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
            <TextField
              name="title"
              label="Title"
              value={formData.title}
              onChange={handleChange}
              required
              fullWidth
            />
            
            <TextField
              name="description"
              label="Description"
              value={formData.description}
              onChange={handleChange}
              multiline
              rows={4}
              fullWidth
            />

            <FormControl fullWidth>
              <InputLabel>Priority</InputLabel>
              <Select
                name="priority"
                value={formData.priority}
                onChange={handleChange}
                label="Priority"
              >
                {priorityOptions.map((option) => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <FormControl fullWidth>
              <InputLabel>Assignee</InputLabel>
              <Select
                name="assignee_id"
                value={formData.assignee_id}
                onChange={handleChange}
                label="Assignee"
              >
                <MenuItem value="">
                  <em>None</em>
                </MenuItem>
                {users.map((user) => (
                  <MenuItem key={user.id} value={user.id}>
                    {user.full_name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <DateTimePicker
              label="Due Date"
              value={formData.due_date}
              onChange={handleDateChange}
              renderInput={(params) => <TextField {...params} fullWidth />}
              fullWidth
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose}>Cancel</Button>
          <Button type="submit" variant="contained" color="primary">
            Save Changes
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default EditTaskModal;
