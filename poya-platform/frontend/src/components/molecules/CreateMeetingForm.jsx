import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  Typography,
  Alert,
  LinearProgress,
  Autocomplete,
  Divider,
  IconButton,
  Chip,
} from '@mui/material';
import { DateTimePicker } from '@mui/x-date-pickers';
import {
  Add as AddIcon,
  Remove as RemoveIcon,
  DragHandle as DragIcon,
} from '@mui/icons-material';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import { createMeeting, clearError, clearSuccess } from '../../store/meetingSlice';

const CreateMeetingForm = ({ open, onClose, users }) => {
  const dispatch = useDispatch();
  const { loading, error, success } = useSelector((state) => state.meetings);
  const [formData, setFormData] = useState({
    title: '',
    purpose: '',
    start_time: null,
    end_time: null,
    location: '',
    attendee_ids: [],
    agenda_items: [],
  });

  useEffect(() => {
    if (success) {
      setTimeout(() => {
        dispatch(clearSuccess());
        handleClose();
      }, 1500);
    }
  }, [success, dispatch]);

  const handleClose = () => {
    setFormData({
      title: '',
      purpose: '',
      start_time: null,
      end_time: null,
      location: '',
      attendee_ids: [],
      agenda_items: [],
    });
    dispatch(clearError());
    onClose();
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleDateChange = (field) => (date) => {
    setFormData((prev) => ({
      ...prev,
      [field]: date,
    }));
  };

  const handleAttendeeChange = (event, newValue) => {
    setFormData((prev) => ({
      ...prev,
      attendee_ids: newValue.map((user) => user.id),
    }));
  };

  const handleAddAgendaItem = () => {
    setFormData((prev) => ({
      ...prev,
      agenda_items: [
        ...prev.agenda_items,
        { topic: '', description: '', duration_minutes: 15 },
      ],
    }));
  };

  const handleRemoveAgendaItem = (index) => {
    setFormData((prev) => ({
      ...prev,
      agenda_items: prev.agenda_items.filter((_, i) => i !== index),
    }));
  };

  const handleAgendaItemChange = (index, field) => (e) => {
    const newAgendaItems = [...formData.agenda_items];
    newAgendaItems[index] = {
      ...newAgendaItems[index],
      [field]: e.target.value,
    };
    setFormData((prev) => ({
      ...prev,
      agenda_items: newAgendaItems,
    }));
  };

  const onDragEnd = (result) => {
    if (!result.destination) return;

    const items = Array.from(formData.agenda_items);
    const [reorderedItem] = items.splice(result.source.index, 1);
    items.splice(result.destination.index, 0, reorderedItem);

    setFormData((prev) => ({
      ...prev,
      agenda_items: items,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    await dispatch(createMeeting(formData));
  };

  const isValid = formData.title &&
                 formData.purpose &&
                 formData.start_time &&
                 formData.end_time &&
                 formData.location &&
                 formData.attendee_ids.length > 0;

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <form onSubmit={handleSubmit}>
        <DialogTitle>Schedule New Meeting</DialogTitle>
        <DialogContent>
          {loading && <LinearProgress />}
          
          <Box display="flex" flexDirection="column" gap={3} mt={2}>
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
              label="Meeting Title"
              value={formData.title}
              onChange={handleChange}
              fullWidth
              required
            />

            <TextField
              name="purpose"
              label="Meeting Purpose"
              value={formData.purpose}
              onChange={handleChange}
              multiline
              rows={2}
              fullWidth
              required
            />

            <Box display="flex" gap={2}>
              <DateTimePicker
                label="Start Time"
                value={formData.start_time}
                onChange={handleDateChange('start_time')}
                fullWidth
                required
              />
              <DateTimePicker
                label="End Time"
                value={formData.end_time}
                onChange={handleDateChange('end_time')}
                fullWidth
                required
              />
            </Box>

            <TextField
              name="location"
              label="Location"
              value={formData.location}
              onChange={handleChange}
              fullWidth
              required
            />

            <Autocomplete
              multiple
              options={users}
              getOptionLabel={(option) => option.full_name}
              onChange={handleAttendeeChange}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Attendees"
                  required
                />
              )}
              renderTags={(value, getTagProps) =>
                value.map((option, index) => (
                  <Chip
                    label={option.full_name}
                    {...getTagProps({ index })}
                  />
                ))
              }
            />

            <Divider />

            <Box>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="subtitle1">Agenda Items</Typography>
                <Button
                  startIcon={<AddIcon />}
                  onClick={handleAddAgendaItem}
                >
                  Add Item
                </Button>
              </Box>

              <DragDropContext onDragEnd={onDragEnd}>
                <Droppable droppableId="agenda-items">
                  {(provided) => (
                    <Box {...provided.droppableProps} ref={provided.innerRef}>
                      {formData.agenda_items.map((item, index) => (
                        <Draggable
                          key={index}
                          draggableId={`item-${index}`}
                          index={index}
                        >
                          {(provided) => (
                            <Box
                              ref={provided.innerRef}
                              {...provided.draggableProps}
                              sx={{ mb: 2 }}
                            >
                              <Box
                                sx={{
                                  p: 2,
                                  border: 1,
                                  borderColor: 'divider',
                                  borderRadius: 1,
                                }}
                              >
                                <Box display="flex" alignItems="center" gap={1} mb={2}>
                                  <IconButton size="small" {...provided.dragHandleProps}>
                                    <DragIcon />
                                  </IconButton>
                                  <Typography>Item {index + 1}</Typography>
                                  <Box flex={1} />
                                  <IconButton
                                    size="small"
                                    onClick={() => handleRemoveAgendaItem(index)}
                                    color="error"
                                  >
                                    <RemoveIcon />
                                  </IconButton>
                                </Box>

                                <Box display="flex" flexDirection="column" gap={2}>
                                  <TextField
                                    value={item.topic}
                                    onChange={handleAgendaItemChange(index, 'topic')}
                                    label="Topic"
                                    fullWidth
                                    required
                                  />
                                  <TextField
                                    value={item.description}
                                    onChange={handleAgendaItemChange(index, 'description')}
                                    label="Description"
                                    multiline
                                    rows={2}
                                    fullWidth
                                  />
                                  <TextField
                                    type="number"
                                    value={item.duration_minutes}
                                    onChange={handleAgendaItemChange(index, 'duration_minutes')}
                                    label="Duration (minutes)"
                                    InputProps={{ inputProps: { min: 5 } }}
                                    fullWidth
                                  />
                                </Box>
                              </Box>
                            </Box>
                          )}
                        </Draggable>
                      ))}
                      {provided.placeholder}
                    </Box>
                  )}
                </Droppable>
              </DragDropContext>
            </Box>
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
            Schedule Meeting
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default CreateMeetingForm;
