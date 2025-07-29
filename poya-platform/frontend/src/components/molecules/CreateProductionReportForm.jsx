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
  Typography,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';
import { useDispatch, useSelector } from 'react-redux';
import { createProductionReport } from '../../store/productionReportSlice';

const shifts = [
  { value: 'morning', label: 'Morning Shift' },
  { value: 'afternoon', label: 'Afternoon Shift' },
  { value: 'night', label: 'Night Shift' },
];

const stoppageTypes = [
  { value: 'maintenance', label: 'Maintenance' },
  { value: 'breakdown', label: 'Breakdown' },
  { value: 'material_shortage', label: 'Material Shortage' },
  { value: 'setup_changeover', label: 'Setup/Changeover' },
  { value: 'quality_issue', label: 'Quality Issue' },
  { value: 'other', label: 'Other' },
];

const CreateProductionReportForm = ({ open, onClose }) => {
  const dispatch = useDispatch();
  const items = useSelector((state) => state.items.items);
  const [formData, setFormData] = useState({
    report_date: new Date(),
    shift: '',
    daily_challenge: '',
    solutions_implemented: '',
    notes: '',
    production_logs: [],
    stoppages: [],
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
      report_date: date,
    }));
  };

  const addProductionLog = () => {
    setFormData((prev) => ({
      ...prev,
      production_logs: [
        ...prev.production_logs,
        { item_id: '', quantity_produced: 0, target_quantity: 0, remarks: '' },
      ],
    }));
  };

  const addStoppage = () => {
    setFormData((prev) => ({
      ...prev,
      stoppages: [
        ...prev.stoppages,
        { type: '', reason: '', duration: 0, action_taken: '' },
      ],
    }));
  };

  const updateProductionLog = (index, field, value) => {
    setFormData((prev) => ({
      ...prev,
      production_logs: prev.production_logs.map((log, i) =>
        i === index ? { ...log, [field]: value } : log
      ),
    }));
  };

  const updateStoppage = (index, field, value) => {
    setFormData((prev) => ({
      ...prev,
      stoppages: prev.stoppages.map((stoppage, i) =>
        i === index ? { ...stoppage, [field]: value } : stoppage
      ),
    }));
  };

  const removeProductionLog = (index) => {
    setFormData((prev) => ({
      ...prev,
      production_logs: prev.production_logs.filter((_, i) => i !== index),
    }));
  };

  const removeStoppage = (index) => {
    setFormData((prev) => ({
      ...prev,
      stoppages: prev.stoppages.filter((_, i) => i !== index),
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await dispatch(createProductionReport({
        ...formData,
        report_date: formData.report_date.toISOString().split('T')[0],
      })).unwrap();
      onClose();
    } catch (error) {
      console.error('Failed to create production report:', error);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <form onSubmit={handleSubmit}>
        <DialogTitle>Create Production Report</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
            {/* Basic Information */}
            <Box sx={{ display: 'flex', gap: 2 }}>
              <DatePicker
                label="Report Date"
                value={formData.report_date}
                onChange={handleDateChange}
                renderInput={(params) => <TextField {...params} required />}
                sx={{ flex: 1 }}
              />
              
              <FormControl required sx={{ flex: 1 }}>
                <InputLabel>Shift</InputLabel>
                <Select
                  name="shift"
                  value={formData.shift}
                  onChange={handleChange}
                  label="Shift"
                >
                  {shifts.map((shift) => (
                    <MenuItem key={shift.value} value={shift.value}>
                      {shift.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Box>

            <TextField
              name="daily_challenge"
              label="Daily Challenge"
              value={formData.daily_challenge}
              onChange={handleChange}
              multiline
              rows={2}
            />

            <TextField
              name="solutions_implemented"
              label="Solutions Implemented"
              value={formData.solutions_implemented}
              onChange={handleChange}
              multiline
              rows={2}
            />

            {/* Production Logs */}
            <Box>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                <Typography variant="h6">Production Logs</Typography>
                <Button
                  startIcon={<AddIcon />}
                  onClick={addProductionLog}
                  variant="outlined"
                  size="small"
                >
                  Add Item
                </Button>
              </Box>
              
              <TableContainer component={Paper} variant="outlined">
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Item</TableCell>
                      <TableCell align="right">Produced</TableCell>
                      <TableCell align="right">Target</TableCell>
                      <TableCell>Remarks</TableCell>
                      <TableCell />
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {formData.production_logs.map((log, index) => (
                      <TableRow key={index}>
                        <TableCell>
                          <FormControl fullWidth size="small">
                            <Select
                              value={log.item_id}
                              onChange={(e) => updateProductionLog(index, 'item_id', e.target.value)}
                              required
                            >
                              {items.map((item) => (
                                <MenuItem key={item.id} value={item.id}>
                                  {item.name} ({item.item_code})
                                </MenuItem>
                              ))}
                            </Select>
                          </FormControl>
                        </TableCell>
                        <TableCell>
                          <TextField
                            type="number"
                            size="small"
                            value={log.quantity_produced}
                            onChange={(e) => updateProductionLog(index, 'quantity_produced', parseFloat(e.target.value))}
                            required
                          />
                        </TableCell>
                        <TableCell>
                          <TextField
                            type="number"
                            size="small"
                            value={log.target_quantity}
                            onChange={(e) => updateProductionLog(index, 'target_quantity', parseFloat(e.target.value))}
                            required
                          />
                        </TableCell>
                        <TableCell>
                          <TextField
                            size="small"
                            value={log.remarks}
                            onChange={(e) => updateProductionLog(index, 'remarks', e.target.value)}
                          />
                        </TableCell>
                        <TableCell>
                          <IconButton size="small" onClick={() => removeProductionLog(index)}>
                            <DeleteIcon />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>

            {/* Stoppages */}
            <Box>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                <Typography variant="h6">Stoppages</Typography>
                <Button
                  startIcon={<AddIcon />}
                  onClick={addStoppage}
                  variant="outlined"
                  size="small"
                >
                  Add Stoppage
                </Button>
              </Box>
              
              <TableContainer component={Paper} variant="outlined">
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Type</TableCell>
                      <TableCell>Reason</TableCell>
                      <TableCell align="right">Duration (min)</TableCell>
                      <TableCell>Action Taken</TableCell>
                      <TableCell />
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {formData.stoppages.map((stoppage, index) => (
                      <TableRow key={index}>
                        <TableCell>
                          <FormControl fullWidth size="small">
                            <Select
                              value={stoppage.type}
                              onChange={(e) => updateStoppage(index, 'type', e.target.value)}
                              required
                            >
                              {stoppageTypes.map((type) => (
                                <MenuItem key={type.value} value={type.value}>
                                  {type.label}
                                </MenuItem>
                              ))}
                            </Select>
                          </FormControl>
                        </TableCell>
                        <TableCell>
                          <TextField
                            size="small"
                            value={stoppage.reason}
                            onChange={(e) => updateStoppage(index, 'reason', e.target.value)}
                            required
                          />
                        </TableCell>
                        <TableCell>
                          <TextField
                            type="number"
                            size="small"
                            value={stoppage.duration}
                            onChange={(e) => updateStoppage(index, 'duration', parseFloat(e.target.value))}
                            required
                          />
                        </TableCell>
                        <TableCell>
                          <TextField
                            size="small"
                            value={stoppage.action_taken}
                            onChange={(e) => updateStoppage(index, 'action_taken', e.target.value)}
                          />
                        </TableCell>
                        <TableCell>
                          <IconButton size="small" onClick={() => removeStoppage(index)}>
                            <DeleteIcon />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>

            <TextField
              name="notes"
              label="Additional Notes"
              value={formData.notes}
              onChange={handleChange}
              multiline
              rows={2}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose}>Cancel</Button>
          <Button
            type="submit"
            variant="contained"
            color="primary"
            disabled={formData.production_logs.length === 0}
          >
            Create Report
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default CreateProductionReportForm;
